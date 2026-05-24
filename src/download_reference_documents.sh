#!/bin/bash
# Download reference documents for sexual violence analysis

set -e

OUTPUT_DIR="data/sources/reference_documents"
mkdir -p "$OUTPUT_DIR"

echo "Downloading reference documents..."

# 1. MIR Sexual violence synthesis report
echo "1. Downloading MIR sexual violence synthesis report..."
curl -L "https://onvios.ses.mir.es/publico/onvios/dam/jcr:9942a4db-e162-4ba6-bb25-30a73a97261b/Estudio%20sobre%20la%20violencia%20sexual%20en%20Espa%C3%B1a.%20Una%20s%C3%ADntesis%20estimativa.pdf" \
  -o "$OUTPUT_DIR/MIR_SexualViolence_Synthesis.pdf" 2>/dev/null &

# 2. CCOO analysis report
echo "2. Downloading CCOO analysis..."
curl -L "https://www.ccoo.es/f00e29e47111cb7cc0a26a8eb59ac845000045.pdf" \
  -o "$OUTPUT_DIR/CCOO_Analysis.pdf" 2>/dev/null &

# 3. MIR Violence against women 2015-2019 report
echo "3. Downloading MIR violence against women 2015-2019..."
curl -L "https://onvios.ses.mir.es/publico/onvios/dam/jcr:ad20ce96-5965-4528-bec6-c7b92e4d6ac2/Informe_sobre_-violencia_-contra_-la-mujer_-2015-2019_126210076.pdf" \
  -o "$OUTPUT_DIR/MIR_ViolenceWomen_2015-2019.pdf" 2>/dev/null &

# 4. MIR Group sexual violence report (2023)
echo "4. Downloading MIR group sexual violence report..."
curl -L "https://onvios.ses.mir.es/publico/onvios/dam/jcr:97f2b828-4f37-4845-8f78-d718539c62c6/Informe%20sobre%20violencia%20sexual%20en%20grupo.%2025.10.2023_NIPO.pdf" \
  -o "$OUTPUT_DIR/MIR_GroupSexualViolence_2023.pdf" 2>/dev/null &

# Wait for all downloads to complete
wait
echo "✓ All reference documents downloaded to $OUTPUT_DIR/"
ls -lh "$OUTPUT_DIR/"
