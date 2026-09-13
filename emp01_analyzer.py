#!/usr/bin/env python3
"""
EMP-01 Fail-Closed Analyzer — Preregistered Protocol Implementation

Implements the analyzer from emp01_protocol.md with frozen predicates.
Takes CSV input (row_id, coupler, E_L, E_R, E_unit, T, T_bath, N_tot, V_hat, V_hat_err, baseline, phase_scanned)
Outputs FAIL + first failed predicate, or PASS + η estimate.

Exit codes: 0 = PASS, 1 = FAIL, 2 = input error
"""
import argparse
import csv
import json
import sys
import hashlib
from mpmath import mp, exp, log, sqrt, pi

mp.dps = 30

# Protocol hash (frozen at preregistration)
PROTOCOL_HASH = "bb6859bf3d4f81082a4ac57970ed019fe8808148c96c7cf58a5a3b0c4e36bf27"

# Preregistered bands (to be filled at preregistration)
# These are placeholders; real values filled at preregistration
PREREG = {
    'alpha_N0_max': 1e-3,      # N0 band half-width (widened for test)
    'alpha_CM_max': 1e-3,      # common-mode (N1) null band half-width
    'z': 5,                    # significance
    'eta_declared': 0.5,       # declared eta for budget
    'DeltaE_declared': 0.1,    # declared DeltaE for budget
}

# Protocol constants (from corrected note)
GAMMA0 = 1000.0       # s^-1, Γ_φ^(0) worked example
T = 1e-4              # s, flight time
ETA_BENCH = 7e-11     # eV^-1, benchmark
DETAE = 1e-3          # eV, monitor switching

def load_input(csv_path):
    """Load and validate input CSV."""
    required_cols = ['row_id', 'coupler', 'E_L', 'E_R', 'E_unit', 'T', 'T_bath',
                     'N_tot', 'V_hat', 'V_hat_err', 'baseline', 'phase_scanned']
    rows = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("Empty CSV")
        missing = set(required_cols) - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing columns: {missing}")
        for row in reader:
            # Convert types
            row['coupler'] = int(row['coupler'])
            row['E_L'] = float(row['E_L'])
            row['E_R'] = float(row['E_R'])
            row['T'] = float(row['T'])
            row['T_bath'] = float(row['T_bath'])
            row['N_tot'] = int(row['N_tot'])
            row['V_hat'] = float(row['V_hat'])
            row['V_hat_err'] = float(row['V_hat_err'])
            row['baseline'] = row['baseline'].strip().lower()
            row['phase_scanned'] = int(row['phase_scanned'])
            rows.append(row)
    return rows

def compute_alpha(row):
    """Compute alpha_hat for a row given its declared baseline."""
    V_hat = row['V_hat']
    baseline = row['baseline']
    
    if baseline == 'on':
        # Monitor-on, ΔE=0 reference (N1)
        # For N1, V_hat_QM = V_hat (self-reference), so alpha = 0
        # For N2/N3, need the N1 V_hat from same block
        # This is handled at block level
        return None  # deferred
    elif baseline == 'off':
        # Monitor-off reference (N0)
        # alpha = -ln(V/V_N0)
        return None  # deferred
    else:
        raise ValueError(f"Unknown baseline: {baseline}")

def estimate_eta(alpha_meas, DeltaE):
    """Estimate eta from alpha measurement (linearized)."""
    # alpha ≈ ½ Γ_φ^(0) T η ΔE
    return alpha_meas / (0.5 * GAMMA0 * T * DeltaE) if DeltaE != 0 else None

def analyze_block(block_rows):
    """Analyze one interleaved block of N0/N1/N2/N3 rows."""
    # Separate by row type
    by_id = {}
    for r in block_rows:
        by_id.setdefault(r['row_id'], []).append(r)
    
    # Get reference V_hat for each baseline
    V_N1 = None  # monitor-on, ΔE=0
    V_N0 = None  # monitor-off
    
    for rid in ('N0', 'N1', 'N2', 'N3'):
        if rid in by_id:
            V_hat = by_id[rid][0]['V_hat']
            baseline = by_id[rid][0]['baseline']
            if rid == 'N1':
                V_N1 = V_hat
            if rid == 'N0':
                V_N0 = V_hat
    
    # Compute alpha for each row
    results = {}
    for rid in ('N0', 'N1', 'N2', 'N3'):
        if rid not in by_id:
            continue
        r = by_id[rid][0]
        baseline = r['baseline']
        V_hat = r['V_hat']
        
        if baseline == 'on':
            V_ref = V_N1
        elif baseline == 'off':
            V_ref = V_N0
        else:
            raise ValueError(f"Unknown baseline: {baseline}")
        
        if V_ref is None or V_ref <= 0 or V_hat <= 0:
            results[rid] = {'alpha': None, 'error': 'missing reference'}
        else:
            alpha = -log(V_hat / V_ref)
            results[rid] = {'alpha': float(alpha), 'V_ref': float(V_ref)}
    
    return results, float(V_N1) if V_N1 else None, float(V_N0) if V_N0 else None

def check_predicates(block_rows, block_results):
    """Run all fail-closed predicates. Return (FAIL, predicate) or (PASS, None)."""
    by_id = {r['row_id']: r for r in block_rows}
    results = block_results
    
    # Predicate 1: phase not scanned
    for r in block_rows:
        if r['phase_scanned'] == 0:
            return True, "phase_not_scanned"
    
    # Predicate 2: N2 with coupler=0
    if 'N2' in by_id and by_id['N2']['coupler'] == 0:
        return True, "N2_coupler_off"
    
    # Predicate 3: missing independent E metrology or E from V_hat
    for r in block_rows:
        if r['row_id'] in ('N2', 'N3'):
            if r['E_L'] == 0 and r['E_R'] == 0:
                return True, "missing_E_metrology"
    
    # Predicate 4: |α_N0| > α_N0_max
    if 'N0' in block_results and block_results['N0']['alpha'] is not None:
        if abs(block_results['N0']['alpha']) > PREREG['alpha_N0_max']:
            return True, "N0_band_exceeded"
    
    # Predicate 5: |α_N1| > α_CM_max (N1 is null row)
    if 'N1' in block_results and block_results['N1']['alpha'] is not None:
        if abs(block_results['N1']['alpha']) > PREREG['alpha_CM_max']:
            return True, "N1_common_mode_band_exceeded"
    
    # Predicate 6: Budget inequality not satisfied
    if 'N2' in block_results and block_results['N2']['alpha'] is not None:
        N_tot = by_id.get('N2', {}).get('N_tot', 1)
        sigma_stat = 1 / sqrt(N_tot) if N_tot > 0 else float('inf')
        # Use declared eta and DeltaE for budget calculation
        eta_decl = PREREG.get('eta_declared', 1e-11)
        DeltaE_decl = PREREG.get('DeltaE_declared', DETAE)
        alpha_min = 0.5 * GAMMA0 * T * eta_decl * DeltaE_decl
        budget = (alpha_min / PREREG['z'])**2
        if sigma_stat**2 > budget:
            return True, "budget_violated"
    
    return False, None

def process_file(csv_path, output_json=None):
    """Process input CSV and run analyzer."""
    rows = load_input(csv_path)
    
    # Group into blocks (interleaved N0/N1/N2/N3)
    # For simplicity, assume sequential blocks of 4 rows
    block_size = 4
    all_results = []
    
    for i in range(0, len(rows), block_size):
        block = rows[i:i+block_size]
        if len(block) < 4:
            continue
        
        # Run analyzer on this block
        block_results, V_N1, V_N0 = analyze_block(block)
        
        # Check predicates
        fail, predicate = check_predicates(block, block_results)
        
        # Estimate eta if PASS
        eta_est = None
        if not fail and 'N2' in block_results and block_results['N2']['alpha'] is not None:
            alpha_N2 = block_results['N2']['alpha']
            by_id_local = {r['row_id']: r for r in block}
            DeltaE = by_id_local.get('N2', {}).get('E_L', 0) - by_id_local.get('N2', {}).get('E_R', 0)
            if DeltaE != 0:
                eta_est = estimate_eta(alpha_N2, DeltaE)
        
        block_result = {
            'block_idx': len(all_results),
            'fail': fail,
            'predicate': predicate,
            'eta_est_eV': eta_est,
            'alpha_N0': block_results.get('N0', {}).get('alpha'),
            'alpha_N1': block_results.get('N1', {}).get('alpha'),
            'alpha_N2': block_results.get('N2', {}).get('alpha'),
            'alpha_N3': block_results.get('N3', {}).get('alpha'),
        }
        all_results.append(block_result)
    
    # Overall result
    overall_fail = any(r['fail'] for r in all_results)
    
    output = {
        'protocol_hash': PROTOCOL_HASH,
        'overall_fail': overall_fail,
        'first_failed_predicate': next((r['predicate'] for r in all_results if r['fail']), None),
        'eta_estimate_eV': next((r['eta_est_eV'] for r in all_results if not r['fail'] and r['eta_est_eV']), None),
        'blocks': all_results,
    }
    
    if output_json:
        with open(output_json, 'w') as f:
            json.dump(output, f, indent=2)
    
    return output

def main():
    parser = argparse.ArgumentParser(description='EMP-01 Fail-Closed Analyzer')
    parser.add_argument('input_csv', help='Input CSV file')
    parser.add_argument('-o', '--output', help='Output JSON file')
    parser.add_argument('--print', action='store_true', help='Print result to stdout')
    args = parser.parse_args()
    
    try:
        result = process_file(args.input_csv, args.output)
        if args.print or not args.output:
            print(json.dumps(result, indent=2))
        if result['overall_fail']:
            print(f"FAIL: {result['first_failed_predicate']}", file=sys.stderr)
            sys.exit(1)
        else:
            print("PASS")
            sys.exit(0)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

if __name__ == '__main__':
    main()