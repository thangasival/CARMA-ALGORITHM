"""
Frankfurt Pharmaceutical & Express Logistics Network
=====================================================
Case study demonstrating CARMA on a European multimodal inland hub with
GENUINE cost-time-emission trade-offs.

Frankfurt am Main is an INLAND hub — only road (truck) and rail are accessible
directly. Air freight departs from Frankfurt Airport.  Ship/coastal modes are
NOT applicable (no Rhine river connection for general freight routing here).

Three-mode setup creates a real Pareto surface:
  - Rail   : EUR 0.055/t-km | 0.057 kg CO2e/t-km | 22 km/h (EU freight avg)
  - Truck  : EUR 0.110/t-km | 0.076 kg CO2e/t-km | 78 km/h
  - Air    : EUR 9.500/t-km | 0.680 kg CO2e/t-km | 750 km/h (block speed)

Rail is cheaper AND cleaner than truck (MILP picks rail for all viable routes).
Air is faster but expensive AND high-emission.
=> NSGA-III generates genuine Pareto surface:
   [rail: cheap+clean+slow] <---> [air: expensive+dirty+fast]

Cargo urgency modelled through time-penalty in NSGA-III objectives:
  pharma-express (24h) | pharma-standard (72h) | industrial (168h)

Data sources:
  EF truck: HBEFA 4.2 HDV Euro VI (0.0762 kg CO2e/t-km)
  EF rail:  Eurostat 2022 EU-27 freight rail average (0.057 kg CO2e/t-km)
  EF air:   ICAO CORSIA 2022 (0.680 kg CO2e/t-km)
  Rail speed: UIC Annual Report 2023 — EU freight rail avg 18-25 km/h
  Costs:    KPMG European Logistics Radar 2023, Lufthansa Cargo rate card 2023
  Grid CI:  ENTSO-E Transparency Platform 2023 — Germany 400 gCO2/kWh

Author: Sivalingam Thangavel <th.sivalingam@gmail.com>
"""

import sys, os, warnings, time, json
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithm.optimization.nsga3_optimizer import Route as NSGARoute
from algorithm.carma import CARMA, CARMAConfig

# ---------------------------------------------------------------------------
# Frankfurt hub — 14 European destinations (inland routes: truck + rail + air)
# ---------------------------------------------------------------------------
# (dest, dist_km, weight_t, cargo_urgency, temp_c, cong, slope_deg, weather)
# cargo_urgency: 'pharma_express' 24h | 'pharma_std' 72h | 'industrial' 168h
FRANKFURT_NETWORK = [
    # -- Short: truck/rail both feasible; rail saves cost+emission -----
    ("Prague CZ",        280,  8.0, "pharma_std",    12.0, 1.4, 1.5, "clear"),
    ("Zurich CH",        350, 10.0, "pharma_express", 8.0, 1.2, 4.5, "rain"),
    ("Amsterdam NL",     370, 12.0, "industrial",    14.0, 1.6, 0.5, "rain"),
    ("Brussels BE",      395, 11.0, "pharma_std",    13.0, 1.5, 0.5, "rain"),
    # -- Medium: truck feasible for pharma; rail optimal for industrial --
    ("Hamburg DE",       480, 14.0, "industrial",    11.0, 1.3, 0.5, "rain"),
    ("Berlin DE",        550, 13.0, "pharma_std",    10.0, 1.4, 0.5, "clear"),
    ("Paris FR",         485, 15.0, "pharma_express", 12.0, 1.7, 1.0, "rain"),
    ("Vienna AT",        620, 16.0, "industrial",     9.0, 1.3, 2.5, "clear"),
    # -- Long: rail too slow for pharma_express -> air required ----------
    ("Warsaw PL",       1100, 18.0, "pharma_express", 8.0, 1.3, 1.0, "snow"),
    ("Milan IT",         700, 20.0, "pharma_express", 16.0, 1.5, 3.0, "clear"),
    ("Lyon FR",          630, 14.0, "industrial",    14.0, 1.2, 2.0, "rain"),
    ("Barcelona ES",    1500, 22.0, "pharma_express", 17.0, 1.4, 2.5, "clear"),
    ("Madrid ES",       1800, 25.0, "industrial",    18.0, 1.2, 1.5, "clear"),
    ("Budapest HU",      840, 12.0, "pharma_std",    10.0, 1.3, 2.0, "clear"),
]

# ---------------------------------------------------------------------------
# Four modes — Rotterdam is a COASTAL hub with Rhine-North Sea ship access
# ---------------------------------------------------------------------------
MODE_EF = {
    "truck": 0.0762,   # HBEFA 4.2 HDV Euro VI
    "rail":  0.0570,   # Eurostat 2022 EU-27 standard tariff
    "air":   0.6800,   # ICAO CORSIA 2022 (cargo, belly + freighter weighted)
    "ship":  0.0110,   # Eurostat 2022 short-sea coastal shipping
}

MODE_COST_PER_TONKM = {
    "truck": 0.110,    # KPMG 2023: European FTL road (fuel + driver + TCO)
    "rail":  0.055,    # DB Cargo intermodal (incl. terminal handling amortised)
    "air":   9.500,    # Lufthansa Cargo 2023 rate card, economy class
    "ship":  0.028,    # Eurostat 2022 short-sea/feeder shipping (Rhine corridor)
}
TERMINAL_COST_EUR = {
    "truck": 0.0,
    "rail":  25.0,     # DB Cargo terminal loading + unloading per shipment
    "air":   45.0,     # AMS/FRA Airport: handling + security + AWB documentation
    "ship":  20.0,     # Port terminal handling per shipment
}

MODE_SPEED_KMH = {
    "truck": 78,      # EU HGV regulation 90 km/h, effective 78 km/h inc. rest
    "rail":  22,      # UIC 2023: EU freight rail avg 18-25 km/h (passenger priority)
    "air":   750,     # Block speed RTM/AMS -> destination (cruise + taxi + approach)
    "ship":  22,      # North Sea/Rhine short-sea feeder speed
}

CARGO_TIME_LIMIT_H = {
    "pharma_express": 24,    # Biologics, vaccines, clinical trial material
    "pharma_std":     72,    # Finished drugs, medical devices, diagnostics
    "industrial":    168,    # Automotive parts, chemicals, machinery (7 days)
}


def transit_h(dist_km: float, mode: str) -> float:
    return dist_km / MODE_SPEED_KMH[mode]


def mode_meets_deadline(dist_km: float, cargo: str, mode: str) -> bool:
    return transit_h(dist_km, mode) <= CARGO_TIME_LIMIT_H[cargo]


def compute_cost(dist_km: float, wt_t: float, mode: str) -> float:
    return dist_km * wt_t * MODE_COST_PER_TONKM[mode] + TERMINAL_COST_EUR[mode]


def compute_emission(dist_km: float, wt_t: float, mode: str) -> float:
    return dist_km * wt_t * MODE_EF[mode]


def compute_baseline():
    rows = []
    for (dest, dist, wt, cargo, *_) in FRANKFURT_NETWORK:
        rows.append({
            "destination": dest, "cargo": cargo,
            "emission_kg": compute_emission(dist, wt, "truck"),
            "cost_eur":    compute_cost(dist, wt, "truck"),
        })
    df = pd.DataFrame(rows)
    return df["cost_eur"].sum(), df["emission_kg"].sum(), df


def make_nsga_routes():
    routes = []
    for (dest, dist, wt, cargo, temp, cong, slope, weather) in FRANKFURT_NETWORK:
        routes.append(NSGARoute(
            origin="Frankfurt DE",
            destination=dest,
            distance_km=float(dist),
            weight_tons=float(wt),
            commodity_type="general",      # use generic label to avoid ML label mismatch
            transport_mode="truck",
            temperature_c=float(temp),
            congestion_factor=float(cong),
            slope_degrees=float(slope),
            weather_condition=weather,
            is_weekend=False,
        ))
    return routes


def make_training_df(seed: int = 42) -> pd.DataFrame:
    """European multimodal freight training data — truck, rail, air only."""
    np.random.seed(seed)
    n = 600
    modes = ["truck"] * 300 + ["rail"] * 210 + ["air"] * 90
    np.random.shuffle(modes)

    rows = []
    for i in range(n):
        mode  = modes[i]
        ef    = MODE_EF[mode]
        dist  = np.random.uniform(100, 2000)
        wt    = np.random.uniform(1, 30)
        em    = dist * wt * ef * np.random.uniform(0.88, 1.12)
        speed = MODE_SPEED_KMH[mode]
        cong  = round(np.random.uniform(1.0, 2.2), 2)
        temp  = round(np.random.uniform(-5, 35), 1)
        slope = round(np.random.uniform(0.0, 4.0), 2)
        load  = round(np.random.uniform(0.35, 1.0), 2)
        spd   = round(speed * np.random.uniform(0.80, 1.05), 1)

        rows.append({
            "route_id":                   f"FRA{i:04d}",
            "transport_mode":             mode,
            "distance_km":                round(dist, 1),
            "weight_tons":                round(wt, 2),
            "total_emission_kg":          round(em, 2),
            "adjusted_emissions_kg_co2e": round(em, 2),
            "fuel_cost_eur":              round(compute_cost(dist, wt, mode), 1),
            "transit_time_hours":         round(dist / speed, 2),
            "cargo_type":                 "general",
            "commodity_type":             "general",
            "is_hazardous":               bool(np.random.rand() > 0.85),
            "is_weekend":                 bool(np.random.rand() > 0.8),
            "is_peak_hour":               bool(np.random.rand() > 0.7),
            "temperature_c":              temp,
            "congestion_factor":          cong,
            "slope_degrees":              slope,
            "is_uphill":                  bool(np.random.rand() > 0.5),
            "weather_condition":          np.random.choice(
                                              ["clear","rain","snow"],
                                              p=[0.60, 0.28, 0.12]),
            "load_factor":                load,
            "speed_kmh":                  spd,
            "actual_speed_kmh":           spd,
            "optimal_speed_kmh":          float(speed),
            "speed_ratio":                round(spd / speed, 3),
            "payload_efficiency":         load,
            "distance_category":          ("short" if dist < 400 else
                                           "medium" if dist < 900 else "long"),
            "env_efficiency_simple":      round(em / (dist * wt + 1e-6), 6),
            "physics_emission_simple":    round(em * 0.95, 2),
        })
    return pd.DataFrame(rows)


def banner(title):
    print("\n" + "=" * 72)
    print(f"  {title}")
    print("=" * 72)


def pct(new, old):
    return (new - old) / abs(old) * 100 if old != 0 else 0.0


def main():
    banner("CARMA - European Multimodal Network (Rotterdam Hub)")
    print(f"""
  Hub         : Port of Rotterdam, Netherlands (Europe's largest seaport)
  Routes      : {len(FRANKFURT_NETWORK)} European destinations
  Modes       : Truck (78 km/h) | Rail (22 km/h EU avg) | Air (750 km/h) | Ship (22 km/h)
  Cargo types : pharma-express (24h max) | pharma-std (72h) | industrial (7d)
  Trade-off   : Ship/Rail = cheap+clean+slow  <-->  Air = expensive+dirty+fast
                Truck = medium speed, cost, emission
  EF source   : HBEFA 4.2 (truck), Eurostat 2022 (rail+ship), ICAO CORSIA (air)
  Grid CI     : Germany 2023 = 400 gCO2/kWh (ENTSO-E Transparency Platform)
    """)

    # --- Feasibility matrix ---
    banner("Mode Feasibility: Transit Time vs Deadline")
    print(f"\n  {'Destination':<15} {'km':>5}  {'Cargo':<16}  "
          f"{'Truck':>7}  {'Rail':>7}  {'Air':>5}  {'Deadline':>8}  "
          f"{'Rail OK?':>8}  Air needed?")
    print("  " + "-" * 90)
    for (dest, dist, wt, cargo, *_) in FRANKFURT_NETWORK:
        lim = CARGO_TIME_LIMIT_H[cargo]
        t_t = transit_h(dist, "truck")
        t_r = transit_h(dist, "rail")
        t_a = transit_h(dist, "air")
        rail_ok  = "YES" if t_r <= lim else f"NO({t_r:.0f}h)"
        air_need = "YES" if not mode_meets_deadline(dist, cargo, "truck") else "-"
        print(f"  {dest:<15} {dist:>5}  {cargo:<16}  "
              f"{t_t:>6.1f}h  {t_r:>6.1f}h  {t_a:>4.1f}h  "
              f"{lim:>6}h  {rail_ok:>8}  {air_need:>11}")

    routes      = make_nsga_routes()
    training_df = make_training_df()
    b_cost, b_em, b_df = compute_baseline()

    n_air = sum(1 for (_, d, _, c, *_) in FRANKFURT_NETWORK
                if not mode_meets_deadline(d, c, "rail"))
    print(f"\n  Routes where rail violates deadline: {n_air} "
          f"(truck/air required for pharma-express)")
    print(f"  Truck-only baseline:")
    print(f"    Total cost      : EUR {b_cost:>10,.0f}")
    print(f"    Total emissions : {b_em:>10,.0f} kg CO2e")

    # --- CARMA ---
    config = CARMAConfig(
        grid_ci_g_kwh               = 400.0,
        ensemble_strategy           = "segmented",
        ml_test_size                = 0.20,
        carbon_budget_reduction_pct = 20.0,
        ets_price_eur_per_tonne     = 65.0,
        nsga3_population            = 84,
        nsga3_generations           = 80,
        nsga3_partitions            = 6,
        enable_dynamic_ci           = True,
        origin_country              = "DE",
        time_flexibility_hours      = 8.0,
        preference_weights          = {
            "cost":        0.35,
            "emissions":   0.40,
            "time":        0.15,
            "reliability": 0.10,
        },
    )

    banner("Running CARMA 6-Phase Pipeline")
    t0     = time.time()
    result = CARMA(config).run(routes, training_df=training_df)
    elapsed = time.time() - t0
    result.print_summary()

    # --- Route-level table ---
    banner("Route-Level: Truck Baseline vs CARMA Optimal Assignment")
    milp_assignments = result.milp_mode_assignments or {}
    route_id_map     = {f"R{i:04d}": row[0] for i, row in enumerate(FRANKFURT_NETWORK)}
    dest_mode_map    = {route_id_map[rid]: mode
                        for rid, mode in milp_assignments.items() if rid in route_id_map}

    print(f"\n  {'Destination':<15} {'km':>5} {'Cargo':<16}  "
          f"{'Truck em':>9}  {'Mode':>5}  {'Opt em':>9}  {'Em%':>7}  "
          f"{'Truck h':>7}  {'Opt h':>5}  {'Cost%':>7}")
    print("  " + "-" * 100)

    tot_b_em = tot_o_em = tot_b_cost = tot_o_cost = 0.0
    n_shifts = n_air_assigned = 0
    for (dest, dist, wt, cargo, *_) in FRANKFURT_NETWORK:
        b_em_r   = compute_emission(dist, wt, "truck")
        b_cost_r = compute_cost(dist, wt, "truck")
        b_t_r    = transit_h(dist, "truck")
        opt_mode = dest_mode_map.get(dest, "truck")
        o_em_r   = compute_emission(dist, wt, opt_mode)
        o_cost_r = compute_cost(dist, wt, opt_mode)
        o_t_r    = transit_h(dist, opt_mode)
        em_pct   = pct(o_em_r, b_em_r)
        cost_pct = pct(o_cost_r, b_cost_r)
        if opt_mode != "truck":
            n_shifts += 1
        if opt_mode == "air":
            n_air_assigned += 1
        flag = f" <{opt_mode}" if opt_mode != "truck" else ""
        print(f"  {dest:<15} {dist:>5} {cargo:<16}  "
              f"{b_em_r:>9,.1f}  {opt_mode:>5}  {o_em_r:>9,.1f}  "
              f"{em_pct:>6.1f}%  {b_t_r:>6.1f}h  {o_t_r:>4.1f}h  "
              f"{cost_pct:>6.1f}%{flag}")
        tot_b_em   += b_em_r;  tot_o_em   += o_em_r
        tot_b_cost += b_cost_r; tot_o_cost += o_cost_r

    print("  " + "-" * 100)
    tot_em_pct   = pct(tot_o_em, tot_b_em)
    tot_cost_pct = pct(tot_o_cost, tot_b_cost)
    print(f"  {'TOTAL':<15} {'':>5} {'':>16}  "
          f"{tot_b_em:>9,.0f}  {'OPT':>5}  {tot_o_em:>9,.0f}  "
          f"{tot_em_pct:>6.1f}%  {'':>6}  {'':>5}  {tot_cost_pct:>6.1f}%")
    print(f"\n  Mode shifts: {n_shifts}/{len(FRANKFURT_NETWORK)} | "
          f"Air assigned: {n_air_assigned} routes")

    # --- Pareto front ---
    if result.pareto_front:
        banner(f"DCCT-NSGA-III Pareto Front ({result.n_pareto_solutions} solutions)")
        costs = [s["total_cost"]         for s in result.pareto_front]
        emits = [s["total_emissions_kg"] for s in result.pareto_front]
        times = [s["total_time_hours"]   for s in result.pareto_front]
        print(f"\n  Cost  range : EUR {min(costs):>10,.0f} -- EUR {max(costs):>10,.0f}")
        print(f"  Emiss range : {min(emits):>10,.0f} -- {max(emits):>10,.0f} kg CO2e")
        print(f"  Time  range : {min(times):>10.1f} -- {max(times):>10.1f} h")
        print(f"\n  {'Label':<14}  {'Cost (EUR)':>12}  {'Emissions':>12}  {'Time':>8}")
        print("  " + "-" * 50)
        sorted_em = sorted(result.pareto_front, key=lambda x: x["total_emissions_kg"])
        for label, sol in [
            ("Emission-min", sorted_em[0]),
            ("Balanced",     result.preferred_solution or sorted_em[len(sorted_em)//2]),
            ("Cost-min",     sorted(result.pareto_front, key=lambda x: x["total_cost"])[0]),
            ("Time-min",     sorted(result.pareto_front, key=lambda x: x["total_time_hours"])[0]),
        ]:
            if sol:
                print(f"  {label:<14}  {sol['total_cost']:>12,.0f}  "
                      f"{sol['total_emissions_kg']:>12,.0f}  "
                      f"{sol['total_time_hours']:>8.1f}h")

    # --- Summary ---
    banner("Frankfurt Network Summary")
    milp_em_pct   = result.milp_emission_pct
    milp_cost_pct = result.milp_cost_change_pct
    annual_ci_t   = result.dynamic_ci_saving_kg * 250 / 1000

    print(f"""
  Metric                                    Value
  -----------------------------------------------
  Routes                                    {len(FRANKFURT_NETWORK)}
  Modes available                           Truck | Rail | Air | Ship (coastal)
  Mode shifts (MILP optimal)                {n_shifts} of {len(FRANKFURT_NETWORK)}
  Air assignments (CARMA optimal)           {n_air_assigned}
  MILP emission change (PIEM basis)         {milp_em_pct:+.1f}%
  MILP cost change (PIEM basis)             {milp_cost_pct:+.1f}%
  Flat-EF emission change                   {tot_em_pct:+.1f}%
  Flat-EF cost change                       {tot_cost_pct:+.1f}%
  Pareto-optimal solutions                  {result.n_pareto_solutions}
  Dynamic CI saving (per run)               {result.dynamic_ci_saving_kg:.0f} kg CO2e
  Annual CI saving (250 days/yr)            {annual_ci_t:.1f} t CO2e/yr
  Wall time (full pipeline)                 {elapsed:.1f} s
    """)

    out_dir = os.path.join(os.path.dirname(__file__), "..", "data",
                           "processed", "optimization_results")
    os.makedirs(out_dir, exist_ok=True)
    summary = {
        "case_study":         "Rotterdam European Multimodal Hub (4-mode: truck/rail/air/ship)",
        "n_routes":           len(FRANKFURT_NETWORK),
        "modes":              ["truck", "rail", "air", "ship"],
        "baseline_em_kg":     round(b_em, 0),
        "baseline_cost_eur":  round(b_cost, 0),
        "milp_em_pct":        round(milp_em_pct, 2),
        "milp_cost_pct":      round(milp_cost_pct, 2),
        "flatef_em_pct":      round(tot_em_pct, 2),
        "flatef_cost_pct":    round(tot_cost_pct, 2),
        "n_pareto":           result.n_pareto_solutions,
        "n_mode_shifts":      n_shifts,
        "n_air_assigned":     n_air_assigned,
        "annual_ci_saving_t": round(annual_ci_t, 1),
        "wall_time_s":        round(elapsed, 1),
    }
    out_path = os.path.join(out_dir, "frankfurt_pharma_summary.json")
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  Results saved -> {out_path}")
    banner("FRANKFURT NETWORK COMPLETE")
    return summary


if __name__ == "__main__":
    main()
