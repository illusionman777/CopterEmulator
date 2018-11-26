from study_module import Environment


if __name__ == '__main__':
    env = Environment()
    env.reset(0)
    env.step([512, 512, 512, 512])
    env.step([512, 512, 512, 512])
    env = 0
    a = 1
