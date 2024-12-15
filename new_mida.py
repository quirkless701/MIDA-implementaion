import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Define a simple Requester class for task requesters in MCS
class Requester:
    def __init__(self, name, budget, num_tasks, task_complexity, floor_price, ceil_price):
        self.name = name
        self.budget = budget
        self.num_tasks = num_tasks
        self.task_complexity = task_complexity  # Complexity of the task (e.g., reward or difficulty)
        self.bid_price = random.uniform(floor_price, ceil_price)  # Random bid price within the floor and ceiling prices
        self.remaining_budget = budget  # Track remaining budget after allocation
        self.floor_price = floor_price  # The minimum price requester is willing to pay per task
        self.ceil_price = ceil_price  # The maximum price requester is willing to pay per task

    def __repr__(self):
        return f"Requester({self.name}, Budget: {self.budget}, Tasks: {self.num_tasks}, Bid: {self.bid_price:.2f})"

# Define a simple Provider class for mobile users providing task completion
class Provider:
    def __init__(self, name, capacity, ask_price, quality, floor_price, ceil_price):
        self.name = name
        self.capacity = capacity  # Max tasks they can perform
        self.ask_price = random.uniform(floor_price, ceil_price)  # Random ask price within floor and ceiling
        self.quality = quality  # Quality of the data they provide (0 to 1)
        self.tasks_completed = 0  # Track tasks completed for this provider
        self.floor_price = floor_price  # The minimum price provider is willing to accept
        self.ceil_price = ceil_price  # The maximum price provider can charge

    def __repr__(self):
        return f"Provider({self.name}, Capacity: {self.capacity}, Ask: {self.ask_price:.2f}, Quality: {self.quality:.2f})"

# Define initial parameters
num_requesters = 50
num_providers = 1000
num_simulations = 1000
floor_price = 10  # Set minimum price for both requesters and providers
ceil_price = 30  # Set maximum price for both requesters and providers

# Function to split requesters and providers based on task complexity and provider characteristics
def split_market(requesters, providers):
    # Sort requesters based on task complexity (low to high)
    requesters_sorted = sorted(requesters, key=lambda r: r.task_complexity)
    
    # Sort providers based on ask price and quality (low price and high quality first)
    providers_sorted = sorted(providers, key=lambda p: (p.ask_price, -p.quality))
    
    # Split requesters into two halves (based on task complexity)
    left_requesters = requesters_sorted[:len(requesters_sorted)//2]
    right_requesters = requesters_sorted[len(requesters_sorted)//2:]
    
    # Split providers into two halves (balanced by price and quality)
    left_providers = providers_sorted[:len(providers_sorted)//2]
    right_providers = providers_sorted[len(providers_sorted)//2:]
    
    return left_requesters, right_requesters, left_providers, right_providers

# Function to calculate the equilibrium price
def calculate_equilibrium_price(requesters, providers):
    bid_prices = [r.bid_price for r in requesters]
    ask_prices = [p.ask_price for p in providers]
    
    # Calculate the equilibrium price considering price and quality of providers
    weighted_provider_prices = [p.ask_price * p.quality for p in providers]  # Quality-weighted prices
    average_bid_price = np.mean(bid_prices)
    average_provider_price = np.mean(weighted_provider_prices) / np.mean([p.quality for p in providers])  # Normalize by quality

    equilibrium_price = (average_bid_price + average_provider_price) / 2
    return equilibrium_price


# Updated function to allocate tasks and track additional metrics
def allocate_tasks_with_metrics(requesters, providers, equilibrium_price):
    total_payout_to_requesters = 0
    total_payout_to_providers = 0
    total_value_generated = 0

    for requester in requesters:
        tasks_to_allocate = requester.num_tasks
        for provider in providers:
            if (provider.ask_price >= provider.floor_price and provider.ask_price <= provider.ceil_price and
                requester.bid_price >= requester.floor_price and requester.bid_price <= requester.ceil_price and
                provider.ask_price <= equilibrium_price and provider.capacity > 0 and provider.quality >= 0.7 and tasks_to_allocate > 0):
                
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

# Run task allocation for multiple simulations with metrics tracking
def run_simulations_with_metrics(num_simulations):
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

        # Allocate tasks and collect metrics
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

# Run the simulations and collect the metrics
results = run_simulations_with_metrics(1000)

# Metrics and labels
metrics = ['Task Completion Rate', 'Budget Usage', 'Gain from Trade', 
           'Payout to Requesters', 'Payout to Providers', 'Quality-Adjusted Completion']
values = results
colors = ['skyblue', 'salmon', 'lightgreen', 'gold', 'violet', 'cyan']

# Create a grid of subplots
fig, axes = plt.subplots(2, 3, figsize=(15, 10))  # 2 rows and 3 columns
axes = axes.flatten()  # Flatten axes for easier iteration

# Plot each metric in its respective subplot
for i, (metric, value, color) in enumerate(zip(metrics, values, colors)):
    axes[i].bar([metric], [value], color=color)
    axes[i].set_ylim(0, 100 if 'Rate' in metric or 'Usage' in metric else None)  # Adjust y-axis range
    axes[i].set_ylabel('Percentage' if 'Rate' in metric or 'Usage' in metric else 'Value')
    axes[i].set_title(metric)

# Adjust layout
plt.tight_layout()
plt.show()

# Print the results for clarity
print(f"Average Task Completion Rate: {results[0]:.2f}%")
print(f"Average Budget Usage: {results[1]:.2f}%")
print(f"Average Gain from Trade: {results[2]:.2f}")
print(f"Average Payout to Requesters: {results[3]:.2f}")
print(f"Average Payout to Providers: {results[4]:.2f}")
print(f"Average Quality-Adjusted Completion Rate: {results[5]:.2f}%")
