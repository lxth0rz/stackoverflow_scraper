# Stack Overflow Users URLs

This actor allows you to scrape the users URLs from Stack Overflow.

## Input configuration

The actor has the following input options:

- **Scrape By** - Select the type of users you would like to collect their URLs. 
You can select one from the following list... 
```python
["Reputation", "New users", "Voters", "Editors", "Moderators"]
```

- **Filter By Time** - Select the time period...
```python
["week", "month", "quarter", "year", "all"]
```

- **Proxy** - Optionally, select a proxy to be used by the actor,
  in order to avoid IP address-based blocking by the target website.
  The actor automatically executes all the Scrapy's HTTP(S) requests through the proxy.