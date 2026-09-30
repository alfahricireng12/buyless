# Behavioral evaluation scenarios

`scenarios.json` contains realistic requests and expected observable behavior. It is an evaluation plan, not a claim that an AI host has passed these cases.

The 24 scenarios include dynamic discovery without store/country lists, local scripts, destination restrictions, non-two-decimal currencies, coverage limits, copied evidence, self-proclaimed official sellers and serial-number overclaims. Named locations are test inputs, not a supported-country list.

To evaluate a host, load BuyLess using that host's supported skill mechanism. Give it one scenario's request and the specified tool/source conditions. Record whether it follows location requirements, preserves the price objective, distinguishes unknown costs, cites evidence, and respects action boundaries.

Use mocked or shareable sources for repeatable cases. Do not contact sellers, create accounts, purchase items, or spend on API access solely to run these cases without authorization. A browser-enabled live run is a separate check and should include its date, tools, coverage, and limitations.

Score each expected behavior as pass/fail/not-observable. Retain the actual output and explain failures. Do not describe scenario definitions or helper unit tests as a measured model benchmark.
