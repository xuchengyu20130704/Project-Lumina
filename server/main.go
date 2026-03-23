package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"github.com/sashabaranov/go-openai"
)

func main() {
	// 1. 尝试加载当前目录下的 .env
	if err := godotenv.Load(".env"); err != nil {
		fmt.Println("![注意]: 未能在当前目录找到 .env，将尝试从系统环境变量读取。")
	}

	apiKey := os.Getenv("SILICONFLOW_API_KEY")
	if apiKey == "" {
		log.Fatal("![系统核心错误]: 缺少 SILICONFLOW_API_KEY，星轨无法对齐。")
	}

	r := gin.Default()

	// 2. 核心路由：对话
	r.POST("/chat", func(c *gin.Context) {
		var req struct {
			Message string `json:"message" binding:"required"`
		}
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"reply": "![系统]: 信号输入非法。"})
			return
		}

		// 初始化指向硅基流动的客户端
		config := openai.DefaultConfig(apiKey)
		config.BaseURL = "https://api.siliconflow.cn/v1"
		client := openai.NewClientWithConfig(config)

		resp, err := client.CreateChatCompletion(context.Background(), openai.ChatCompletionRequest{
			Model: "Qwen/Qwen3-8B",
			Messages: []openai.ChatCompletionMessage{
				{Role: "system", Content: "你是‘微光’。准则：禁止废话，主次分明，直击要点。"},
				{Role: "user", Content: req.Message},
			},
			Temperature: 0.7,
		})

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"reply": "![链路故障]: " + err.Error()})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"reply": resp.Choices[0].Message.Content,
		})
	})

	fmt.Println("![微光]: 核心系统已就绪，监听 127.0.0.1:8000")
	r.Run(":8000")
}
