DEX fight
===

Python price bot for multiple Dex.

Based on [multidex-python](https://github.com/0xfffangel/multidex-python).

### Install
```bash
python3 -m virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Example
Example dexs fight on BSC chain
```bash
# BNB/BUSD
python main.py --base BNB --input 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c --output 0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56
python main.py --base BNB --output 0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56

# BNB/USDT
python main.py --base BNB --input 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c --output 0x55d398326f99059fF775485246999027B3197955
python main.py --base BNB --output 0x55d398326f99059fF775485246999027B3197955

# CAKE/BNB
python main.py --base BNB --input 0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82 --output 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c
python main.py --base BNB --input 0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82

# MBOX/BNB
python main.py --base BNB --input 0x3203c9E46cA618C8C1cE5dC67e7e9D75f5da2377 --output 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c
python main.py --base BNB --input 0x3203c9E46cA618C8C1cE5dC67e7e9D75f5da2377

# USDT/BUSD
python main.py --base BNB --input 0x55d398326f99059fF775485246999027B3197955 --output 0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56

# GLMR/BUSD
python main.py --base GLMR --output 0xa649325aa7c5093d12d6f98eb4378deae68ce23f
```