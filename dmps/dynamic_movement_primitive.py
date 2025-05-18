import numpy as np
from scipy.interpolate import CubicSpline

from .canonical_system import CanonicalSystem


class DynamicMovementPrimitive:

    def __init__(self, dt, n_dmps=1, n_bfs=10, ay=None, by=None, **kwargs):
        self.n_dmps = n_dmps
        self.n_bfs = n_bfs
        self.cs = CanonicalSystem(dt=dt, ax=kwargs.get("ax",1.0))
        self.w = None
        self.ay = np.repeat(25.0, n_dmps) if ay is None else np.asarray(ay)
        self.by = self.ay/4.0 if by is None else np.asarray(by)
        if self.ay.shape == ():
            self.ay = np.repeat(self.ay, n_dmps)
        if self.by.shape == ():
            self.by = np.repeat(self.by, n_dmps)
        assert self.ay.shape == (n_dmps,)
        assert self.by.shape == (n_dmps,)
        self.g0 = None
        self.y0 = None
        self.bfs_centers = None
        self.bfs_h = None

    def gen_psi(self, x, canonical=True):
        if isinstance(x, np.ndarray):
            x = x[:,None]
        v = -1./self.cs.ax * np.log(x) if canonical else x
        return np.exp(self.bfs_h*(v - self.bfs_centers)**2) 

    def _gen_bfs_parameters(self):
        self.bfs_centers = np.linspace(0, self.cs.run_time, self.n_bfs)
        sigma = self.cs.run_time/(self.n_bfs)
        self.bfs_h = - 1./(2*sigma**2)

    def _gen_weights(self, ftarget):
        timesteps, x = self.cs.rollout(length=ftarget.shape[0])
        psi = self.gen_psi(x)
        xpsi = (x*psi.T).T
        self.w = np.zeros((self.n_bfs, self.n_dmps))
        for i in range(self.n_dmps):
            scale = self.g0[i] - self.y0[i]
            for b in range(self.n_bfs):
                num = np.sum(xpsi[:,b]*ftarget[:,i])
                den = np.sum(x*xpsi[:,b])
                self.w[b,i] = num/den
                if scale > 1e-6:
                    self.w[b,i] /= scale


    def _prepare_trajectory(self, y, dt):
        if len(y.shape) == 1:
            assert self.n_dmps == 1
            y = y.reshape((len(y), 1))
        else:
            assert len(y.shape) == 2 and y.shape[1] == self.n_dmps
        timesteps = self.cs.timesteps(length=y.shape[0])
        if np.abs(dt - self.cs.dt) > 1e-12:
            t = np.arange(len(y))*dt
            path = np.zeros((len(timesteps), self.n_dmps))
            for i in range(self.n_dmps):
                spl = CubicSpline(t, y[:,i])
                path[:,i] = spl(timesteps)
            y = path
        return timesteps, y

    def fit(self, y, dt=None, plot=False):
        if dt is None:
            dt = self.cs.dt
        T = (len(y)-1)*dt
        T = int(T/self.cs.dt)*self.cs.dt
        self.cs.run_time = T

        self._gen_bfs_parameters()

        timesteps, y = self._prepare_trajectory(y, dt)
        
        yd = np.gradient(y, self.cs.dt, axis=0)
        ydd = np.gradient(yd, self.cs.dt, axis=0)

        self.y0 = y[0]
        self.g0 = y[-1]

        ftarget = np.zeros_like(y)

        for i in range(self.n_dmps):
            ftarget[:,i] = ydd[:,i] - self.ay[i]*(self.by[i]*(self.g0[i]-y[:,i]) - yd[:,i])

        self._gen_weights(ftarget)

        if plot:
            import matplotlib.pyplot as plt
            x = self.cs.convert_to_x(timesteps)
            psi = self.gen_psi(x)
            sum_psi = np.sum(psi, axis=1)
            scale = self.g0 - self.y0
            for i in range(self.n_dmps):
                f = np.dot(self.w[:,i], psi.T)*x/sum_psi
                if scale[i] > 1e-6:
                    f *= scale[i]
                plt.plot(timesteps, f)
            plt.title("forcing term")
            plt.figure()
            plt.plot(timesteps, ftarget)
            plt.title("ftarget")
            plt.show()

    def step(self, y, yd, y0=None, g=None, x=1.0, tau=1.0):
        if y0 is None:
            y0 = self.y0
        if g is None:
            g = self.g0

        x = self.cs.next(x, tau=tau)

        psi = self.gen_psi(x)
        sum_psi = np.sum(psi)

        ydd_next = np.zeros_like(y)
        scale = g - y0
        for i in range(self.n_dmps):
            f = np.dot(self.w[:,i], psi)*x/sum_psi
            if scale[i] > 1e-6:
                f *= scale[i]
            ydd_next[i] = ( self.ay[i]*(self.by[i]*(g[i] - y[i]) - tau*yd[i]) + f )
        ydd_next /= tau*tau
        yd_next = yd + ydd_next*self.cs.dt
        y_next = y + yd_next*self.cs.dt

        return x, y_next, yd_next, ydd_next

    def rollout(self, y0=None, yd0=None, g=None, x=1.0, tau=1.0):
        if y0 is None:
            y0 = self.y0
        if yd0 is None:
            yd0 = np.zeros_like(y0)
        if g is None:
            g = self.g0

        t = [0]
        y = [y0]
        yd = [yd0]
        ydd = [np.zeros(self.n_dmps)]

        while t[-1] < self.cs.run_time*tau:
            x, y_next, yd_next, ydd_next = self.step(y[-1], yd[-1], y0, g, x, tau)
            t.append(t[-1] + self.cs.dt)
            y.append(y_next)
            yd.append(yd_next)
            ydd.append(ydd_next)

        return t, np.array(y), np.array(yd), np.array(ydd)


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    dmp = DynamicMovementPrimitive(dt=0.01, n_bfs=100, n_dmps=1, ay=25)

    t = np.arange(0, 201) * 0.03
    y = 1 + np.sin(2*np.pi*0.5*t)

    dmp.fit(y, dt=0.03, plot=True)

    # print(dmp.w)

    # plt.plot(timesteps, y)
    # plt.plot(timesteps, yd)
    # plt.plot(timesteps, ydd)
    # plt.show()

    # plt.plot(timesteps, ftarget)
    # plt.show()


    tr, x = dmp.cs.rollout(tau=1.0)

    psi = dmp.gen_psi(x)

    for i in range(dmp.n_bfs):
        plt.plot(tr, psi[:,i])
    # plt.gca().invert_xaxis()

    plt.show()

    t_hat, y_hat, yd, ydd = dmp.rollout(tau=10)
    print(y_hat)

    plt.plot(t, y)
    plt.plot(t_hat, y_hat)
    plt.show()
