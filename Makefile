.PHONY: zip clean

zip: "./output/OmniNX Downloader.zip"

"./output/OmniNX Downloader.zip":
	@echo "Creating OmniNX Downloader.zip..."
	@mkdir -p output
	@rm -rf "output/OmniNX Downloader"
	@mkdir -p "output/OmniNX Downloader"
	@cp package.ini "output/OmniNX Downloader/"
	@rsync -av --exclude='RELEASE*.ini' --exclude='*.pyc' --exclude='__pycache__' --exclude='.DS_Store' include/ "output/OmniNX Downloader/include/"
	@cd output && zip -r "OmniNX Downloader.zip" "OmniNX Downloader" \
		-x "*.pyc" \
		-x "__pycache__/*" \
		-x ".DS_Store" \
		-x "*/.DS_Store"
	@rm -rf "output/OmniNX Downloader"
	@echo "✓ Created output/OmniNX Downloader.zip"

clean:
	@rm -f "output/OmniNX Downloader.zip"
	@rm -rf "output/OmniNX Downloader"
	@echo "✓ Cleaned up output/OmniNX Downloader.zip"
