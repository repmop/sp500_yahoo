#!/bin/bash
trap ' ' INT
[[ ":$PATH:" != *":`python3 -m site --user-base`/bin:"* ]] && PATH="`python3 -m site --user-base`/bin:${PATH}"
source venv/bin/activate
python scrape.py
deactivate
grep -Hoe '[0-9]*\.[0-9]*%' *-summary.json
cat aggregate_data.json
