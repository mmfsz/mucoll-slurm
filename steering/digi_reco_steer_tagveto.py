# MAIAConfig digi_reco_steer.py with calorimeter cones that skip the hard-process tags (tagveto_coning.py).
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tagveto_coning
tagveto_coning.run("digi_reco_steer.py")
