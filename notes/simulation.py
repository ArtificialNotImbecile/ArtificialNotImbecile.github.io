import numpy as np
import matplotlib.pyplot as plt

class SimulationSystem:
    def __init__(self):
        self.sgn = lambda x: 1 if x == 0 else np.sign(x)
        self.satU = lambda x, u: np.clip(x, -u, u)
        self.ssq = lambda x, epsilon: self.sgn(x) * (np.sqrt(abs(x) + epsilon) - np.sqrt(epsilon))
        self.gsat = lambda x_min, x, x_max: np.clip(x, x_min, x_max)

        # Controller parameters
        self.U = 0.4 # reference shaper的变化率，越大越快，但是容易overshoot，单位是 m/s
        self.H = 0.18  # reference shaper的加速时间，越小速度越快, 但是容易overshoot，单位是 s
        self.K = 3.2   # theta的增益，越大矫正越快，但是容易oscillate，和PID里的P一样
        self.lambda_coef = 0.3 # 和PID的I项类似，但是是leaky的，越大越激进
        self.epsilon = 0.01
        self.A = 100 # 最大加速度，单位是 m/s^2
        self.V = 0.5  # 最大速度，单位是 m/s
        self.Z = 0.16 # leaky integrator的饱和值, 单位是 m

        # Add-on algorithm parameters
        self.Q = 0.02 # 细粒度, 正常不用改
        self.r = 0.09 * 1.2  # 降低的距离, 设置成和overshoot一样的值多一点就行
        self.T1 = 0.7 # 到达降低后的值之后持续的时间(见论文Fig.9更清晰)
        self.T2 = 0.7 # 从降低的值到设定值的时间

        # System parameters
        self.m = 0.15  # payload mass
        self.l = 0.38  # cable length
        self.g = 9.81  # gravitational acceleration

        # Simulation parameters
        self.T = 0.002
        self.t_end = 10
        self.t = np.arange(0, self.t_end, self.T)
        self.N = len(self.t)

        # Initialize variables
        self.pd = np.zeros(self.N)  # desired position
        self.pd[self.N // 5:] = 1  # 相当于在第N//5个点开始给定要走的路程
        self.pr = np.zeros(self.N) # reference position
        self.rho = np.zeros(self.N) # 内部变量
        self.pp = np.zeros(self.N) # plant position
        self.ac = np.zeros(self.N) # command acceleration
        self.vc = np.zeros(self.N) # command velocity
        self.pc = np.zeros(self.N) # command position
        self.theta = np.zeros(self.N) # sway angle
        self.theta_dot = np.zeros(self.N) # sway angular velocity
        self.pt = np.zeros(self.N) # pt position(防overshot的算法中的pt = pd + b, b < 0)

        # Add-on algorithm variables
        self.B = 0
        self.D = 0
        self.b = 0

    def simulate(self):
        for k in range(1, self.N):
            # Add-on algorithm
            if abs(self.pd[k] - self.pd[k - 1]) > self.Q * self.T:
                self.B = self.r * (self.pc[k - 1] - self.pd[k])
            else:
                self.B = self.B

            if 0 <= self.B < self.pc[k - 1] - self.pd[k]:
                self.D = 0
            elif self.pc[k - 1] - self.pd[k] < self.B <= 0:
                self.D = 0
            else:
                self.D = self.D + self.T

            if 0 <= self.D < self.T1:
                self.b = self.B
            elif self.T1 <= self.D < self.T1 + self.T2:
                self.b = self.b - self.T * self.B / self.T2
            else:
                self.b = 0

            # Reference shaper
            self.pt[k] = self.pd[k] + self.b
            self.pr[k] = self.pr[k - 1] + self.T * self.satU((self.pd[k] + self.b - self.pr[k - 1]) / (self.T + self.H), u=self.U)

            # Nonlinear leaky integrator
            rho_star = self.rho[k - 1] + self.T * self.theta[k - 1]
            self.rho[k] = self.satU(rho_star - self.T * self.lambda_coef * self.ssq(rho_star, (np.sqrt(self.epsilon) + self.T * self.lambda_coef / 2) ** 2), u=self.Z / self.K)
            self.pp[k] = self.pr[k] + self.K * self.rho[k]

            # Command shaper
            ac_star = ((self.pp[k] - self.pc[k - 1]) / self.T - self.vc[k - 1]) / self.T
            self.ac[k] = self.gsat(max(-self.A, (-self.vc[k - 1] - self.V) / self.T), ac_star, min(self.A, (-self.vc[k - 1] + self.V) / self.T))
            self.vc[k] = self.vc[k - 1] + self.T * self.ac[k]
            self.pc[k] = self.pc[k - 1] + self.T * self.vc[k]

            # Update theta using linearized Lagrangian equation of motion
            theta_ddot = -self.g / self.l * self.theta[k - 1] - self.ac[k] / self.l
            self.theta_dot[k] = self.theta_dot[k - 1] + self.T * theta_ddot
            self.theta[k] = self.theta[k - 1] + self.T * self.theta_dot[k]

    def plot_results(self):
        plt.figure(figsize=(10, 8))

        plt.subplot(2, 1, 1)
        plt.plot(self.t, self.pd, label='Desired Position')
        plt.plot(self.t, self.pc, label='Command Position')
        plt.plot(self.t, self.pt, label='pt Position')
        plt.plot(self.t, self.vc, label='Velocity')

        plt.xlabel('Time (s)')
        plt.ylabel('Position')
        plt.legend()
        plt.grid()

        plt.subplot(2, 1, 2)
        plt.plot(self.t, self.theta, label='Sway Angle')
        plt.xlabel('Time (s)')
        plt.ylabel('Sway Angle (rad)')
        plt.legend()
        plt.grid()

        plt.tight_layout()
        plt.show()

system = SimulationSystem()
system.simulate()
system.plot_results()