#!/bin/bash

# Full Forensic Agent Benchmark Pipeline
# Generates incidents, runs benchmark, analyzes results, uploads to Fuseki

set -e

echo "======================================================================"
echo "FORENSIC AGENT - FULL BENCHMARK PIPELINE"
echo "======================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Generate incidents
echo -e "${YELLOW}[1/5] Generating 100 synthetic incidents...${NC}"
python3 generate_incidents.py
echo -e "${GREEN}✓ Incidents generated${NC}"
echo ""

# Step 2: Run benchmark
echo -e "${YELLOW}[2/5] Running forensic analysis on 100 incidents...${NC}"
echo "This will take approximately 25-45 minutes depending on your hardware"
echo ""
python3 run_benchmark.py
echo -e "${GREEN}✓ Benchmark completed${NC}"
echo ""

# Step 3: Analyze results
echo -e "${YELLOW}[3/5] Analyzing results...${NC}"
python3 analyze_results.py
echo -e "${GREEN}✓ Analysis completed${NC}"
echo ""

# Step 4: Upload to Fuseki
echo -e "${YELLOW}[4/5] Uploading systems to Fuseki...${NC}"
python3 upload_to_fuseki.py
echo -e "${GREEN}✓ Upload completed${NC}"
echo ""

# Step 5: Summary
echo -e "${YELLOW}[5/5] Generating summary...${NC}"
echo ""

# Find latest files
LATEST_STATS=$(ls -t results/benchmark_stats_*.json | head -1)
LATEST_ANALYSIS=$(ls -t results/benchmark_analysis_*.md | head -1)

if [ -f "$LATEST_STATS" ]; then
    echo "Results:"
    echo "  Statistics: $LATEST_STATS"
    echo "  Analysis: $LATEST_ANALYSIS"
    echo ""

    # Extract key metrics
    SUCCESS=$(cat "$LATEST_STATS" | python3 -c "import sys, json; print(json.load(sys.stdin)['summary']['successful'])" 2>/dev/null || echo "N/A")
    SUCCESS_RATE=$(cat "$LATEST_STATS" | python3 -c "import sys, json; print(f\"{json.load(sys.stdin)['summary']['success_rate']:.1f}%\")" 2>/dev/null || echo "N/A")
    MEAN_TIME=$(cat "$LATEST_STATS" | python3 -c "import sys, json; print(f\"{json.load(sys.stdin)['performance']['mean_time']:.2f}s\")" 2>/dev/null || echo "N/A")
    MEAN_CONF=$(cat "$LATEST_STATS" | python3 -c "import sys, json; print(f\"{json.load(sys.stdin)['quality']['mean_confidence']:.3f}\")" 2>/dev/null || echo "N/A")

    echo "Key Metrics:"
    echo "  Successful analyses: $SUCCESS"
    echo "  Success rate: $SUCCESS_RATE"
    echo "  Mean processing time: $MEAN_TIME"
    echo "  Mean confidence: $MEAN_CONF"
    echo ""
fi

echo "======================================================================"
echo "PIPELINE COMPLETED SUCCESSFULLY"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "  1. Review detailed analysis: cat $LATEST_ANALYSIS"
echo "  2. Query systems in Fuseki: http://localhost:3030/aiact"
echo "  3. Compare with Claude Sonnet 4.5 by setting LLM_PROVIDER=anthropic"
echo ""
