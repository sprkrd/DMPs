import numpy as np


class CanonicalSystem:

    def __init__(self, dt, ax=1.0):
        self.dt = dt
        self.ax = ax
        self.run_time = 1.0

    def next(self, x, tau=1.):
        return x * np.exp(-self.ax/tau * self.dt)

    def convert_to_x(self, t, tau=1.):
        return np.exp(-self.ax/tau * t)

    def convert_to_t(self, x, tau=1.):
        return -tau/self.ax * np.log(x)

    def timesteps(self, tau=1., length=None):
        if length is None:
            T = self.run_time * tau
            t = np.arange(int(T/self.dt)+1)*self.dt
        else:
            t = np.arange(length)*self.dt
        return t

    def rollout(self, tau=1., length=None):
        t = self.timesteps(tau, length)
        return t, self.convert_to_x(t, tau)


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    cs = CanonicalSystem(0.02)
    t, x = cs.rollout()
    t_slow, x_slow = cs.rollout(2)
    t_fast, x_fast = cs.rollout(0.5)

    t_step = [0.0]
    x_step = [1.0]
    while x_step[-1] >= x[-1]:
        t_step.append(t_step[-1]+0.02)
        x_step.append(cs.next(x_step[-1], tau=1.))


    plt.plot(t, x, label="normal")
    plt.plot(t_slow, x_slow, label="slow")
    plt.plot(t_fast, x_fast, label="fast")
    plt.plot(t_step, x_step, label="step by step")
    plt.xlabel("t")
    plt.ylabel("x(t)")
    plt.legend()
    plt.show()


