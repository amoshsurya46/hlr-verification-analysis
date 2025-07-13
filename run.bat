@echo off
echo Starting MySQL container...
docker-compose up -d

echo Waiting for MySQL to be ready...
timeout /t 30

echo Installing Python dependencies...
pip install -r requirements.txt

echo Running HLR data parser...
python hlr_parser.py

echo Done! Check your data with:
echo docker exec -it hlr_mysql mysql -u hlruser -phlrpass -e "SELECT * FROM HLRDB.hlr_verification;"