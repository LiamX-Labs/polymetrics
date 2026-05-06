# Quick Setup Guide

## Step 1: Install Dependencies

```bash
# Make sure you're in the right directory
cd /home/william/STRATEGIES/Polymarkets

# Activate your conda environment
conda activate <your-env-name>

# Install requirements
pip install -r requirements.txt
```

## Step 2: Get Your FREE PolygonScan API Key

**This is REQUIRED - the tool won't work without it!**

1. Go to: https://polygonscan.com/apis
2. Click "Register" or "Sign In"
3. Create a free account (just email + password)
4. Once logged in, go to "API-KEYs" in the left menu
5. Click "+ Add" to create a new API key
6. Give it a name like "Polymarket Analyzer"
7. Copy the API key (it will look like: `ABC123DEF456GHI789...`)

## Step 3: Run the Analyzer

```bash
python wallet_analyzer.py YOUR_WALLET_ADDRESS --api-key YOUR_API_KEY
```

### Example:

```bash
python wallet_analyzer.py 0x670aB9580B4e21735dD4c30fEF45bb9f465100C9 --api-key ABC123DEF456GHI789
```

### With Details:

```bash
python wallet_analyzer.py 0x670aB9580B4e21735dD4c30fEF45bb9f465100C9 --api-key YOUR_API_KEY --details
```

## Troubleshooting

### Error: "API Error: NOTOK"
- You need to provide a valid API key
- Get one from https://polygonscan.com/apis (it's free!)

### Error: "Invalid API Key"
- Double-check you copied the full API key
- Make sure there are no spaces before/after the key

### Error: "Max rate limit reached"
- Wait a few seconds and try again
- The free tier has limits, but should be enough for most usage

### No transactions found
- Verify the wallet address is correct
- Make sure the wallet has USDC transactions on Polygon
- Check if you're looking at the right network (Polygon, not Ethereum)

## Tips

1. **Save your API key**: Store it somewhere safe so you don't have to look it up each time
2. **Use --details flag**: See individual transactions to understand what's happening
3. **Check both USDC contracts**: The tool automatically checks both native and legacy USDC
4. **Understand the output**:
   - External transfers = Your real money in/out
   - Trading activity = Polymarket position management
   - Net trading positive = Profitable!

## What to Look For

After running the tool, focus on these numbers:

1. **External Net Balance**:
   - Negative = You withdrew more than deposited (could be profits!)
   - Positive = You still have money in the system

2. **Net Trading**:
   - Positive = Your trading is profitable!
   - Negative = Either losses OR you have open positions

3. **Overall Net Change**:
   - Should match your actual wallet balance changes
   - If confusing, use --details to see all transactions

## Need Help?

Read the full [README.md](README.md) for detailed explanations and example scenarios.
