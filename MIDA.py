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

# Function to allocate tasks to providers based on equilibrium price, capacity, and quality with floor/ceil prices
def allocate_tasks_with_floor_and_ceil(requesters, providers, equilibrium_price):
    for requester in requesters:
        tasks_to_allocate = requester.num_tasks
        for provider in providers:
            # Only allocate if provider's ask price is within the allowed range and meets the equilibrium price
            if (provider.ask_price >= provider.floor_price and provider.ask_price <= provider.ceil_price and
                requester.bid_price >= requester.floor_price and requester.bid_price <= requester.ceil_price and
                provider.ask_price <= equilibrium_price and provider.capacity > 0 and provider.quality >= 0.7 and tasks_to_allocate > 0):
                # Allocate as many tasks as possible within the provider's capacity
                tasks = min(tasks_to_allocate, provider.capacity)
                provider.tasks_completed += tasks
                tasks_to_allocate -= tasks
                requester.remaining_budget -= tasks * equilibrium_price
                provider.capacity -= tasks
                if requester.remaining_budget < equilibrium_price:  # Stop if the requester budget is exhausted
                    break

# Run task allocation for multiple simulations
def run_multiple_simulations(num_simulations):
    total_completion_rate = 0
    total_budget_usage = 0
    
    for _ in range(num_simulations):
        # Create random requesters and providers with varying budgets and task requirements
        requesters = [Requester(f"Requester_{i+1}", budget=random.uniform(100, 300), 
                                num_tasks=random.randint(5, 15), 
                                task_complexity=random.uniform(5, 20), 
                                floor_price=floor_price, ceil_price=ceil_price) for i in range(num_requesters)]
        providers = [Provider(f"Provider_{i+1}", capacity=random.randint(1, 10), 
                              ask_price=random.uniform(floor_price, ceil_price), 
                              quality=random.uniform(0.7, 1.0), 
                              floor_price=floor_price, ceil_price=ceil_price) for i in range(num_providers)]
        
        # Split requesters and providers into two sub-markets
        left_requesters, right_requesters, left_providers, right_providers = split_market(requesters, providers)
        
        # Calculate equilibrium prices for both sub-markets
        equilibrium_price_left = calculate_equilibrium_price(left_requesters, right_providers)
        equilibrium_price_right = calculate_equilibrium_price(right_requesters, left_providers)

        # Run task allocation for both halves using floor and ceiling price limits
        allocate_tasks_with_floor_and_ceil(left_requesters, left_providers, equilibrium_price_right)
        allocate_tasks_with_floor_and_ceil(right_requesters, right_providers, equilibrium_price_left)

        # Collect data for this simulation
        total_tasks_requested = sum([r.num_tasks for r in requesters])
        total_tasks_completed = sum([p.tasks_completed for p in providers])
        average_budget_usage = np.mean([(r.budget - r.remaining_budget) / r.budget for r in requesters])
        
        # Accumulate the results for averaging
        total_completion_rate += (total_tasks_completed / total_tasks_requested) * 100
        total_budget_usage += average_budget_usage * 100

    # Calculate average results
    avg_completion_rate = total_completion_rate / num_simulations
    avg_budget_usage = total_budget_usage / num_simulations
    
    return avg_completion_rate, avg_budget_usage

# Run the simulation for 1000 times
avg_completion_rate, avg_budget_usage = run_multiple_simulations(1000)

# Plotting the results
plt.figure(figsize=(10, 5))

# Task Completion Rate Plot
plt.subplot(1, 2, 1)
plt.bar(['Task Completion Rate'], [avg_completion_rate], color='skyblue')
plt.ylim(0, 100)
plt.ylabel('Completion Rate (%)')
plt.title('Average Task Completion Rate in MCS using MIDA')

# Average Budget Usage Plot
plt.subplot(1, 2, 2)
plt.bar(['Avg Budget Usage'], [avg_budget_usage], color='salmon')
plt.ylim(0, 100)
plt.ylabel('Average Budget Usage (%)')
plt.title('Average Budget Usage per Requester')

plt.tight_layout()
plt.show()

print(f"Average Task Completion Rate: {avg_completion_rate:.2f}%")
print(f"Average Budget Usage per Requester: {avg_budget_usage:.2f}%")
