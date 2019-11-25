stop:
		docker-compose down

test:
		docker-compose build && docker-compose up -d && sleep 10s && python3 TestCase.py