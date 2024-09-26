# Discord 簽到系統

這是一個簡單易用的 Discord 簽到系統，當用戶在群組中發言時，系統會自動紀錄並統計每位用戶的：
- 總簽到次數
- 連續簽到天數
- 頭香次數（首次簽到）

## 功能特點
- **自動簽到**：只要在群組中發言，即可自動進行簽到。
- **簽到統計**：記錄每位用戶的總簽到次數和連續簽到天數。
- **頭香統計**：記錄每日最早發言者的頭香次數。

## 安裝指南

1. **創建 Discord Bot**  
   前往 [Discord Developer Portal](https://discord.com/developers/applications) 創建一個新的機器人帳戶，並將其設為私人使用。
   
2. **獲取 Bot Token**  
   在創建完成後，複製機器人的 Token，並將其填入 `config.yaml` 檔案中，格式如下：
   ```yaml
   token: "YOUR_BOT_TOKEN"
   ```

3. **安裝套件**
   執行以下命令安裝套件，建議於虛擬環境執行，以免和 discord.py 等其他分支衝突。
   ```bash
   pip install -r requirements.txt
   ```

4. **運行系統**  
   執行以下命令啟動簽到系統：
   ```bash
   python main.py
   ```

## 系統需求
- Python 3.8+
- requirements.txt

## 常見問題

### 1. 如何設置機器人為私人？
在 Discord Developer Portal 中，找到機器人設置頁面，並將 "Public Bot" 關閉。

### 2. 簽到的定義是什麼？
只要用戶在群組中發言，系統會自動將該次發言記錄為一次簽到。