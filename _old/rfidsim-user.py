from pyrfidsim.simulation import Simulation

if __name__ == '__main__':
    sim = Simulation()
    sim.ber_model = lambda snr: 0.0
    sim.run()
