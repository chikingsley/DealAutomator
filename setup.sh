#!/bin/bash
if [ ! -f .env ]; then
    cp env.example .env
    echo "Please fill in your API keys in .env"
fi
