from env.env import RoomsEnv
from agents.tabular_q_learning import TempAgent
import gym
from tqdm import tqdm


def train(env, learning_rate=0.001, n_episodes=60000, start_epsilon=1.0, final_epsilon = 0.1, enable_epsilon_decay=True, epsilon_decay_strategy="linear"):

    if epsilon_decay_strategy == "linear":
        epsilon_decay = start_epsilon / (n_episodes / 2)  # reduce the exploration over time
    elif epsilon_decay_strategy == "exp":
        epsilon_decay = (final_epsilon / start_epsilon) ** (1 / n_episodes)

    agent = TempAgent(
        env=env,
        learning_rate=learning_rate,
        initial_epsilon=start_epsilon,
        epsilon_decay=epsilon_decay,
        final_epsilon=final_epsilon,
        epsilon_decay_enabled=enable_epsilon_decay
    )


    env = gym.wrappers.RecordEpisodeStatistics(env, deque_size=n_episodes)

    for episode in tqdm(range(n_episodes)):
        obs, info = env.reset()
        done = False

        # episode
        while not done:
            action = agent.get_action(obs)
            next_obs, reward, terminated, _, info = env.step(action)

            # update the agent
            agent.update(obs, action, reward, terminated, next_obs)

            done = terminated
            obs = next_obs

        agent.decay_epsilon()

    return env, agent