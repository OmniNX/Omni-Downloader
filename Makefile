.PHONY: zip clean

zip: "./output/Omni Downloader.zip"

"./output/Omni Downloader.zip":
	@echo "Creating Omni Downloader.zip..."
	@mkdir -p output
	@rm -rf "output/Omni Downloader"
	@mkdir -p "output/Omni Downloader"
	@cp package.ini "output/Omni Downloader/"
	@rsync -av --exclude='RELEASE*.ini' --exclude='*.pyc' --exclude='__pycache__' --exclude='.DS_Store' include/ "output/Omni Downloader/include/"
	@cd output && zip -r "Omni Downloader.zip" "Omni Downloader" \
		-x "*.pyc" \
		-x "__pycache__/*" \
		-x ".DS_Store" \
		-x "*/.DS_Store"
	@rm -rf "output/Omni Downloader"
	@echo "✓ Created output/Omni Downloader.zip"

clean:
	@rm -f "output/Omni Downloader.zip"
	@rm -rf "output/Omni Downloader"
	@echo "✓ Cleaned up output/Omni Downloader.zip"
