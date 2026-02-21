lsof -t -i :5001 -i :5002 -i :5003 -i :5173 -i :5174 -i :5175 | xargs kill -9
