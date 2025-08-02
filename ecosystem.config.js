const basePath = "/app"; // Changed for Docker environment

module.exports = {
  apps: [
    {
      name: "RM_A1",
      script: `${basePath}/multi_bot_launcher/amoyrm1.py`,
      interpreter: "/usr/local/bin/python", // Standard Python path in Docker
    },
    {
      name: "RM_A2",
      script: `${basePath}/multi_bot_launcher/amoyrm2.py`,
      interpreter: "/usr/local/bin/python",
    },
    {
      name: "RM_A3",
      script: `${basePath}/multi_bot_launcher/amoyrm3.py`,
      interpreter: "/usr/local/bin/python",
    },
    {
      name: "Shell_A1",
      script: `${basePath}/multi_bot_launcher/shell1.py`, 
      interpreter: "/usr/local/bin/python",
    },
    {
      name: "MaidRM_1",
      script: `${basePath}/RM_Partner/Rm_bot_maid/maid1.py`,
      interpreter: "/usr/local/bin/python",
    },
    {
      name: "RM_B1",
      script: `${basePath}/RM_Partner/Rm_bot1/main.py`,
      interpreter: "/usr/local/bin/python",
    },
    {
      name: "SGP_A1",
      script: `${basePath}/SGP1/sgbot.py`,
      interpreter: "/usr/local/bin/python",
    },
        {
      name: "FreeCredit1_Mega888",
      script: `${basePath}/RM_Partner/Rm_FreeCredit_bot1/point.py`,
      interpreter: "/usr/local/bin/python",
    },
    {
      name: "FreeCredit2_Mega888",
      script: `${basePath}/RM_Partner/Rm_FreeCredit_bot1/ubot.py`,
      interpreter: "/usr/local/bin/python",
    },
    {
      name: "UserBotTele_A1",
      script: `${basePath}/UserBotTele/accounts/A1/multi_ubot.py`,
      interpreter: "/usr/local/bin/python",
    },
    {
      name: "UserBotTele_A2",
      script: `${basePath}/UserBotTele/accounts/A2/multi_ubot.py`,
      interpreter: "/usr/local/bin/python",
    },
  ],
};