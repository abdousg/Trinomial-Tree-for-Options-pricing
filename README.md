# Option Pricing using Trinomial Tree

This project implements a trinomial tree model in Python to price European and American options, both calls and puts. It is designed with a clear and modular object-oriented structure, allowing for flexibility and easy extension.

## Objective

The goal is to simulate the evolution of an underlying asset using a trinomial tree, then compute the option’s price through backward induction. This method is particularly useful for American options, which can be exercised before maturity.

## Project Structure

.
├── market.py        # Defines market parameters (S0, r, sigma, etc.)
├── node.py          # Node class representing each point in the tree
├── tree.py          # Builds the trinomial tree and handles pricing logic
├── pricer.py        # Main script to run pricing
├── utils.py         # Utility functions (payoffs, formatting, etc.)
├── README.md        # Project documentation

## Features

- Supports European and American options
- Prices both call and put options
- Object-oriented design (Node, Tree, Market)
- Pricing via backward induction
- Customizable model parameters

## Input Parameters

- S0: Initial asset price
- K: Strike price
- r: Risk-free interest rate
- sigma: Volatility
- T: Time to maturity (in years)
- N: Number of steps in the tree
- option_type: 'call' or 'put'
- exercise_type: 'european' or 'american'

## Methodology

At each node, the tree branches into three possible paths:
- Up: S * u
- Mid (no move): S
- Down: S * d

Risk-neutral probabilities (pu, pm, pd) are computed to ensure arbitrage-free pricing. The option value is obtained by initializing payoffs at maturity and recursively computing expected values backward through the tree.

## How to Run

Run the main script with:

python pricer.py

You can enter parameters interactively or modify the script to test specific scenarios.

## Example Output

European Call Price: 10.42  
American Put Price: 12.05

## Possible Improvements

- Add calculation of Greeks (Delta, Gamma, etc.)
- Support for dividend yield
- Graphical visualization of the tree
- Web interface using Streamlit

## Author

Abdoulaye GAYE  
Quantitative Researcher | Python Developer
