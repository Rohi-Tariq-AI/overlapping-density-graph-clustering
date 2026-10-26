import csv
from pathlib import Path
from graph_clustering.cli import main
from graph_clustering.quality import round_half_up, mean_relative_density_deviation_coefficient
ROOT=Path(__file__).resolve().parents[1]
def test_batch_multiple_graphs_and_densities(tmp_path):
    main(['--graphs',str(ROOT/'data/football.txt'),str(ROOT/'data/karate.txt'),'--densities','0.40','0.45','--output',str(tmp_path),'--verify-with-locked'])
    rows=list(csv.DictReader((tmp_path/'all_experiments.csv').open()))
    assert len(rows)==4
    assert all(row['verified_with_locked']=='True' for row in rows)
    for dataset in ('football','karate'):
        for density in ('density_040','density_045'):
            folder=tmp_path/dataset/density
            assert (folder/'summary.txt').exists()
            assert (folder/'clusters.csv').exists()
            assert (folder/'results.json').exists()
def test_half_up_rounding():
    assert round_half_up(0.215)==0.22
