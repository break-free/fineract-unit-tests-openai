cd /root/fineract-unit-tests-openai
echo -e "\n### Parse & Chunk \n"
python3 chunk.py training/test/
echo -e "\n### Train \n"
python3 train.py

echo -e "\n### Prompt \n"
python3 prompt.py Show_Context <<EOF
Write a unit test for the Parts Java class\n
exit
EOF

echo -e "\n### Parse & Chunk \n"
python3 chunk.py ../fineract/fineract-provider/src/main/java/org/apache/fineract/infrastructure/survey/service/
echo -e "\n### Train \n"
python3 train.py

echo -e "\n### Prompt \n"
python3 prompt.py Show_Context <<EOF
Write a new unit test for getPermissionSql within the WriteSurveyServiceImpl class\n
exit
EOF
