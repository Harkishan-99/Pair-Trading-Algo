from trading_system import System

#settings
#-------------------------------
pair = ['ALK', 'UAL']
thresholds = [-1.75, 1.75] #96%
window = 50
#passing the symbols and running it.
algo = System(pair, thresholds, window)
algo.run()
