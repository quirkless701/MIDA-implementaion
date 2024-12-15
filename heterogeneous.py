import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Define a Requester class with multiple task types
class Requester:
    def __init__(self, name, budget, num_tasks, task_complexity, requested_task_types, floor_price, ceil_price):
        self.name = name
        self.budget = budget
        self.num_tasks = num_tasks
        self.task_complexity = task_complexity
        self.requested_task_types = requested_task_types  # Multiple task types
        self.bid_price = random.uniform(floor_price, ceil_price)
        self.remaining_budget = budget
        self.floor_price = floor_price
        self.ceil_price = ceil_price

    def __repr__(self):
        return f"Requester({self.name}, Budget: {self.budget}, Tasks: {self.num_tasks}, Types: {self.requested_task_types}, Bid: {self.bid_price:.2f})"

# Define a Provider class with supported task types
class Provider:
    def __init__(self, name, capacity, ask_price, quality, supported_task_types, floor_price, ceil_price):
        self.name = name
        self.capacity = capacity
        self.ask_price = random.uniform(floor_price, ceil_price)
        self.quality = quality
        self.supported_task_types = supported_task_types  # Supported task types
        self.tasks_completed = 0
        self.floor_price = floor_price
        self.ceil_price = ceil_price

    def __repr__(self):
        return f"Provider({self.name}, Capacity: {self.capacity}, Quality: {self.quality:.2f}, Supports: {self.supported_task_types})"

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

# Allocate tasks with compatibility for multiple task types
def allocate_tasks_with_metrics(requesters, providers, equilibrium_price):
    total_value_generated = 0
    total_tasks_allocated = 0

    for requester in requesters:
        tasks_to_allocate = requester.num_tasks
        for provider in providers:
            # Check compatibility and quality/price criteria
            if (provider.ask_price <= equilibrium_price and
                any(task_type in provider.supported_task_types for task_type in requester.requested_task_types) and
                provider.capacity > 0 and provider.quality >= 0.7 and tasks_to_allocate > 0):
                tasks = min(tasks_to_allocate, provider.capacity)
                transaction_price = min(equilibrium_price, provider.ask_price)
                
                provider.tasks_completed += tasks
                tasks_to_allocate -= tasks
                requester.remaining_budget -= tasks * transaction_price
                provider.capacity -= tasks
                
                total_value_generated += tasks * (requester.bid_price - transaction_price)
                total_tasks_allocated += tasks
                
                if requester.remaining_budget < equilibrium_price:
                    break

    return total_value_generated, total_tasks_allocated

# Simulate with requesters requesting multiple task types
def run_simulations_with_metrics(num_requesters, num_providers, num_simulations):
    total_completion_rate = 0
    total_budget_usage = 0
    total_gain_from_trade = 0
    total_quality_adjusted_completion = 0
    total_tasks_requested = 0
    total_tasks_completed = 0

    for _ in range(num_simulations):
        task_types = ["Type_A", "Type_B", "Type_C"]  # Define some task types

        # Create requesters with multiple requested task types
        requesters = [Requester(
            f"Requester_{i+1}",
            budget=random.uniform(100, 300),
            num_tasks=random.randint(5, 15),
            task_complexity=random.uniform(5, 20),
            requested_task_types=random.sample(task_types, k=random.randint(1, len(task_types))),  # Random subset
            floor_price=floor_price,
            ceil_price=ceil_price
        ) for i in range(num_requesters)]

        # Create providers with random supported task types
        providers = [Provider(
            f"Provider_{i+1}",
            capacity=random.randint(1, 10),
            ask_price=random.uniform(floor_price, ceil_price),
            quality=random.uniform(0.7, 1.0),
            supported_task_types=random.sample(task_types, k=random.randint(1, len(task_types))),  # Random subset
            floor_price=floor_price,
            ceil_price=ceil_price
        ) for i in range(num_providers)]
        
        left_requesters, right_requesters, left_providers, right_providers = split_market(requesters, providers)
        equilibrium_price_left = calculate_equilibrium_price(left_requesters, right_providers)
        equilibrium_price_right = calculate_equilibrium_price(right_requesters, left_providers)

        left_gain, left_tasks = allocate_tasks_with_metrics(left_requesters, left_providers, equilibrium_price_right)
        right_gain, right_tasks = allocate_tasks_with_metrics(right_requesters, right_providers, equilibrium_price_left)
        
        total_gain_from_trade += left_gain + right_gain
        total_tasks_completed += left_tasks + right_tasks
        
        total_tasks_requested += sum([r.num_tasks for r in requesters])
        total_quality_adjusted_completion += sum([p.tasks_completed * p.quality for p in providers])
        total_budget_usage += np.mean([(r.budget - r.remaining_budget) / r.budget for r in requesters]) * 100
    
    avg_completion_rate = (total_tasks_completed / total_tasks_requested) * 100
    avg_quality_adjusted_completion = (total_quality_adjusted_completion / total_tasks_requested) * 100
    avg_budget_usage = total_budget_usage / num_simulations
    avg_gain_from_trade = total_gain_from_trade / num_simulations

    return avg_completion_rate, avg_budget_usage, avg_gain_from_trade, avg_quality_adjusted_completion

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
                'Quality-Adjusted Completion': results[3]
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

# List of metrics to plot
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
