import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Define a simple Requester class
class Requester:
    def __init__(self, name, budget, num_tasks, task_complexity, floor_price, ceil_price):
        self.name = name
        self.budget = budget
        self.num_tasks = num_tasks
        self.task_complexity = task_complexity
        self.bid_price = random.uniform(floor_price, ceil_price)
        self.remaining_budget = budget
        self.floor_price = floor_price
        self.ceil_price = ceil_price

    def __repr__(self):
        return f"Requester({self.name}, Budget: {self.budget}, Tasks: {self.num_tasks}, Bid: {self.bid_price:.2f})"

# Define a simple Provider class
class Provider:
    def __init__(self, name, capacity, ask_price, quality, floor_price, ceil_price):
        self.name = name
        self.capacity = capacity
        self.ask_price = random.uniform(floor_price, ceil_price)
        self.quality = quality
        self.tasks_completed = 0
        self.floor_price = floor_price
        self.ceil_price = ceil_price

    def __repr__(self):
        return f"Provider({self.name}, Capacity: {self.capacity}, Ask: {self.ask_price:.2f}, Quality: {self.quality:.2f})"

# Define initial parameters
floor_price = 10
ceil_price = 30

# Split the market
def split_market(requesters, providers):
    requesters_sorted = sorted(requesters, key=lambda r: r.task_complexity)
    providers_sorted = sorted(providers, key=lambda p: (p.ask_price, -p.quality))
    left_requesters = requesters_sorted[:len(requesters_sorted)//2]
    right_requesters = requesters_sorted[len(requesters_sorted)//2:]
    left_providers = providers_sorted[:len(providers_sorted)//2]
    right_providers = providers_sorted[len(providers_sorted)//2:]
    return left_requesters, right_requesters, left_providers, right_providers

# Calculate equilibrium price
def calculate_equilibrium_price(requesters, providers):
    bid_prices = [r.bid_price for r in requesters]
    weighted_provider_prices = [p.ask_price * p.quality for p in providers]
    average_bid_price = np.mean(bid_prices)
    average_provider_price = np.mean(weighted_provider_prices) / np.mean([p.quality for p in providers])
    return (average_bid_price + average_provider_price) / 2

# Allocate tasks
def allocate_tasks_with_metrics(requesters, providers, equilibrium_price):
    total_payout_to_requesters = 0
    total_payout_to_providers = 0
    total_value_generated = 0

    for requester in requesters:
        tasks_to_allocate = requester.num_tasks
        for provider in providers:
            if (provider.ask_price <= equilibrium_price and
                provider.capacity > 0 and provider.quality >= 0.7 and tasks_to_allocate > 0):
                tasks = min(tasks_to_allocate, provider.capacity)
                transaction_price = min(equilibrium_price, provider.ask_price)
                payout_to_provider = tasks * transaction_price
                payout_to_requester = tasks * equilibrium_price
                
                provider.tasks_completed += tasks
                tasks_to_allocate -= tasks
                requester.remaining_budget -= payout_to_requester
                provider.capacity -= tasks
                
                total_payout_to_requesters += payout_to_requester
                total_payout_to_providers += payout_to_provider
                total_value_generated += tasks * (requester.bid_price - transaction_price)
                
                if requester.remaining_budget < equilibrium_price:
                    break

    return total_payout_to_requesters, total_payout_to_providers, total_value_generated

# Run simulations with metrics
def run_simulations_with_metrics(num_requesters, num_providers, num_simulations):
    total_completion_rate = 0
    total_budget_usage = 0
    total_gain_from_trade = 0
    total_payout_to_requesters = 0
    total_payout_to_providers = 0
    total_quality_adjusted_completion = 0
    total_tasks_requested = 0
    total_tasks_completed = 0

    for _ in range(num_simulations):
        requesters = [Requester(f"Requester_{i+1}", budget=random.uniform(100, 300), 
                                num_tasks=random.randint(5, 15), 
                                task_complexity=random.uniform(5, 20), 
                                floor_price=floor_price, ceil_price=ceil_price) for i in range(num_requesters)]
        providers = [Provider(f"Provider_{i+1}", capacity=random.randint(1, 10), 
                              ask_price=random.uniform(floor_price, ceil_price), 
                              quality=random.uniform(0.7, 1.0), 
                              floor_price=floor_price, ceil_price=ceil_price) for i in range(num_providers)]
        
        left_requesters, right_requesters, left_providers, right_providers = split_market(requesters, providers)
        equilibrium_price_left = calculate_equilibrium_price(left_requesters, right_providers)
        equilibrium_price_right = calculate_equilibrium_price(right_requesters, left_providers)

        left_metrics = allocate_tasks_with_metrics(left_requesters, left_providers, equilibrium_price_right)
        right_metrics = allocate_tasks_with_metrics(right_requesters, right_providers, equilibrium_price_left)
        
        total_payout_to_requesters += left_metrics[0] + right_metrics[0]
        total_payout_to_providers += left_metrics[1] + right_metrics[1]
        total_gain_from_trade += left_metrics[2] + right_metrics[2]
        
        total_tasks_requested += sum([r.num_tasks for r in requesters])
        total_tasks_completed += sum([p.tasks_completed for p in providers])
        total_quality_adjusted_completion += sum([p.tasks_completed * p.quality for p in providers])
        
        total_budget_usage += np.mean([(r.budget - r.remaining_budget) / r.budget for r in requesters]) * 100
    
    avg_completion_rate = (total_tasks_completed / total_tasks_requested) * 100
    avg_quality_adjusted_completion = (total_quality_adjusted_completion / total_tasks_requested) * 100
    avg_budget_usage = total_budget_usage / num_simulations
    avg_gain_from_trade = total_gain_from_trade / num_simulations
    avg_payout_to_requesters = total_payout_to_requesters / num_simulations
    avg_payout_to_providers = total_payout_to_providers / num_simulations

    return avg_completion_rate, avg_budget_usage, avg_gain_from_trade, avg_payout_to_requesters, avg_payout_to_providers, avg_quality_adjusted_completion

# Run multiple configurations
def run_multiple_configurations(requester_configs, provider_configs, num_simulations):
    results_data = []

    for num_requesters in requester_configs:
        for num_providers in provider_configs:
            results = run_simulations_with_metrics(num_requesters, num_providers, num_simulations)
            results_data.append({
                'Requesters': num_requesters,
                'Providers': num_providers,
                'Task Completion Rate': results[0],
                'Budget Usage': results[1],
                'Gain from Trade': results[2],
                'Payout to Requesters': results[3],
                'Payout to Providers': results[4],
                'Quality-Adjusted Completion': results[5]
            })

    return pd.DataFrame(results_data)

# Define configurations
requester_configs = [10, 50, 100]
provider_configs = [10, 50, 100, 500, 1000]
num_simulations = 1000

# Run experiments
results_df = run_multiple_configurations(requester_configs, provider_configs, num_simulations)

# Save results
results_df.to_csv("simulation_results.csv", index=False)

# Updated list of metrics (excluding payouts)
metrics = ['Task Completion Rate', 'Budget Usage', 'Gain from Trade', 'Quality-Adjusted Completion']

# Create subplots
fig, axes = plt.subplots(2, 2, figsize=(14, 12))  # 2 rows and 2 columns for 4 metrics
axes = axes.flatten()  # Flatten the 2D array of axes for easier iteration

# Plot each metric in its respective subplot
for i, metric in enumerate(metrics):
    for num_requesters in requester_configs:
        # Filter data for the specific number of requesters
        filtered_data = results_df[results_df['Requesters'] == num_requesters]
        axes[i].plot(filtered_data['Providers'], filtered_data[metric], label=f'Requesters: {num_requesters}')
    axes[i].set_title(f'{metric} vs Number of Providers')
    axes[i].set_xlabel('Number of Providers')
    axes[i].set_ylabel(metric)
    axes[i].legend()

# Adjust layout to prevent overlap
plt.tight_layout()

# Show the combined plot
plt.show()
