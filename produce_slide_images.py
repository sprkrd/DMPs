#!/usr/bin/env python3

from dmps.dynamic_movement_primitive import DynamicMovementPrimitive

import numpy as np
import matplotlib.pyplot as plt

plt.style.use("dark_background")


def plot1():
    t = np.linspace(0, 2, 200)

    x = (2*np.pi)**2 * np.sin(2*np.pi*t)
    y = (2*np.pi)**2 * np.cos(2*np.pi*t)

    fig, axes = plt.subplots(ncols=1, nrows=2)

    axes[0].plot(t, x)
    axes[0].set_title("forcing term for x coordinate")
    axes[0].set_xlabel("time (s)")
    axes[0].set_ylabel("acceleration ($m/s^2$)")

    axes[1].plot(t, y)
    axes[1].set_title("forcing term for y coordinate")
    axes[1].set_xlabel("time (s)")
    axes[1].set_ylabel("acceleration ($m/s^2$)")

    plt.tight_layout()
    plt.savefig("slides/img/forcing_term_example.png")

    plt.show()


def plot2():
    t = np.linspace(0, 4, 400)

    x = (2*np.pi)**2 * np.sin(2*np.pi*t)*np.exp(-t)
    y = (2*np.pi)**2 * np.cos(2*np.pi*t)*np.exp(-t)

    fig, axes = plt.subplots(ncols=1, nrows=2)

    axes[0].plot(t, x)
    axes[0].set_title("forcing term for x coordinate")
    axes[0].set_xlabel("time (s)")
    axes[0].set_ylabel("acceleration ($m/s^2$)")

    axes[1].plot(t, y)
    axes[1].set_title("forcing term for y coordinate")
    axes[1].set_xlabel("time (s)")
    axes[1].set_ylabel("acceleration ($m/s^2$)")

    plt.tight_layout()
    plt.savefig("slides/img/vanishing_forcing_term_example.png")

    plt.show()


def plot3():
    dmp = DynamicMovementPrimitive(dt=0.01, n_bfs=20, n_dmps=1, ay=25)
    t = np.arange(0, 201) * 0.01
    y = 1 / (1 + np.exp(-5*(t-1)))
    dmp.fit(y, dt=0.01, plot=True, savefig="slides/img/ftarget_vs_flearned.png")

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
    plt.title("Basis functions")
    plt.xlabel("time (s)")
    plt.ylabel("activation")
    plt.savefig("slides/img/bfs_t.png")
    plt.show()

    for i in range(dmp.n_bfs):
        plt.plot(x, psi[:,i])
    plt.gca().invert_xaxis()
    plt.title("Basis functions (canonical system)")
    plt.xlabel("x")
    plt.ylabel("activation")
    plt.savefig("slides/img/bfs_x.png")
    plt.show()

    t_hat, y_hat, yd, ydd = dmp.rollout(tau=1)

    plt.plot(t, y)
    plt.plot(t_hat, y_hat)
    plt.legend(("Demonstrated trajectory", "Replicated trajectory"))
    plt.xlabel("time (s)")
    plt.ylabel("position (m)")
    plt.savefig("slides/img/dmp_rollout.png")
    plt.show()


def plot4():
    t = np.linspace(0,5,200)
    x = np.linspace(0,1,200)

    x_wrt_t = np.exp(-t)
    t_wrt_x = -np.log(x)

    fig, axes = plt.subplots(nrows=1,ncols=2)
    
    axes[0].plot(t, x_wrt_t)
    axes[0].set_title("Phase variable w.r.t. time")
    axes[0].set_xlabel("time (s)")
    axes[0].set_ylabel("x")

    axes[1].plot(x, t_wrt_x)
    axes[1].set_title("Time w.r.t. phase variable")
    axes[1].set_ylabel("time (s)")
    axes[1].set_xlabel("x")
    axes[1].invert_xaxis()

    plt.tight_layout()
    plt.savefig("slides/img/canonical_system.png")
    plt.show()


# plot1()
# plot2()
# plot3()
plot4()
