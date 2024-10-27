from ai21_tokenizer import Tokenizer

tokenizer = Tokenizer.get_tokenizer()

encoded_text = tokenizer.encode("Amazon BedrockはAWSの生成AIサービスです。")
print(encoded_text)
print(f"Number of Tokens: {len(encoded_text)}")

encoded_text = tokenizer.encode("Amazon Bedrock is AWS's generative AI service")
print(encoded_text)
print("Number of Tokens: {}".format(len(encoded_text)))
