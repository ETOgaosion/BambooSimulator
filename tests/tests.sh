# freq
python -m simulation_bamboo --generate-graphs --spot-instance-trace traces/1h-trace-24.csv --model-size 350M
python -m simulation_nore --generate-graphs --spot-instance-trace traces/1h-trace-24.csv --model-size 350M
python -m simulation_oobleck --generate-graphs --spot-instance-trace traces/1h-trace-24.csv --model-size 350M
python -m simulation_varu --generate-graphs --spot-instance-trace traces/1h-trace-24.csv --model-size 350M

python -m simulation_nore --generate-graphs --spot-instance-trace traces/1h-trace-24.csv --model-size 1.3B
python -m simulation_oobleck --generate-graphs --spot-instance-trace traces/1h-trace-24.csv --model-size 1.3B
python -m simulation_varu --generate-graphs --spot-instance-trace traces/1h-trace-24.csv --model-size 1.3B

python -m simulation_bamboo --generate-graphs --spot-instance-trace traces/6h-trace-24.csv --duration 259200 --model-size 350M
python -m simulation_nore --generate-graphs --spot-instance-trace traces/6h-trace-24.csv --duration 259200 --model-size 350M
python -m simulation_oobleck --generate-graphs --spot-instance-trace traces/6h-trace-24.csv --duration 259200 --model-size 350M
python -m simulation_varu --generate-graphs --spot-instance-trace traces/6h-trace-24.csv --duration 259200 --model-size 350M

python -m simulation_nore --generate-graphs --spot-instance-trace traces/6h-trace-24.csv --duration 259200 --model-size 1.3B
python -m simulation_oobleck --generate-graphs --spot-instance-trace traces/6h-trace-24.csv --duration 259200 --model-size 1.3B
python -m simulation_varu --generate-graphs --spot-instance-trace traces/6h-trace-24.csv --duration 259200 --model-size 1.3B


python -m simulation_bamboo --generate-graphs --spot-instance-trace traces/10m-trace-24.csv --duration 7200 --model-size 350M
python -m simulation_nore --generate-graphs --spot-instance-trace traces/10m-trace-24.csv --duration 7200 --model-size 350M
python -m simulation_oobleck --generate-graphs --spot-instance-trace traces/10m-trace-24.csv --duration 7200 --model-size 350M
python -m simulation_varu --generate-graphs --spot-instance-trace traces/10m-trace-24.csv --duration 7200 --model-size 350M

python -m simulation_nore --generate-graphs --spot-instance-trace traces/10m-trace-24.csv --duration 7200 --model-size 1.3B
python -m simulation_oobleck --generate-graphs --spot-instance-trace traces/10m-trace-24.csv --duration 7200 --model-size 1.3B
python -m simulation_varu --generate-graphs --spot-instance-trace traces/10m-trace-24.csv --duration 7200 --model-size 1.3B