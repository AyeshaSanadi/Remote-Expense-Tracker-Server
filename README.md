Steps to Create Remote server and use it.

1. install uv
2. create new dir
3. open folder in vs code
4. do uv init .
5. uv add fastmcp
6. create a simple server
   for remote server we need to specify the transport, host and port for eg ' mcp.run(transport="http", host="0.0.0.0", port=8000)'
7. run the server using this command ' fastmcp run main.py --transport http --host 0.0.0.0 --port 8000' or 'uv run main.py'
8. open new terminal and Test the server using mcp inspector
9. create github repo and do git add, commit and push
10. create an account on FastMCP cloud (https://horizon.prefect.io)
11. Deploy on FastMCP cloud
12. we got some url like this https://neighbouring-lavender-mole.fastmcp.app/mcp
13. We can connect our remote server to client using 2 ways
a. for pro plan claude users there is one option that is custom connectors which is available inside connect
b. for non pro user we should need to create a proxy server 