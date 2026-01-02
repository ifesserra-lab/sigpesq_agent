"""
Core module for Agent Sigpesq.

Contains fundamental abstractions and factories used throughout the library, 
including the `BaseAgent` and `BrowserFactory`.
"""
from .base_agent import BaseAgent
from .browser_factory import BrowserFactory

__all__ = ["BaseAgent", "BrowserFactory"]
