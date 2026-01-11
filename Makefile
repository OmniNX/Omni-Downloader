.PHONY: zip clean

zip: "Omni Downloader.zip"

"Omni Downloader.zip":
	@echo "Creating Omni Downloader.zip..."
	@rm -rf "Omni Downloader"
	@mkdir -p "Omni Downloader"
	@cp package.ini "Omni Downloader/"
	@rsync -av --exclude='RELEASE*.ini' --exclude='*.pyc' --exclude='__pycache__' --exclude='.DS_Store' include/ "Omni Downloader/include/"
	@zip -r "Omni Downloader.zip" "Omni Downloader" \
		-x "*.pyc" \
		-x "__pycache__/*" \
		-x ".DS_Store" \
		-x "*/.DS_Store"
	@rm -rf "Omni Downloader"
	@echo "✓ Created Omni Downloader.zip"

clean:
	@rm -f "Omni Downloader.zip"
	@rm -rf "Omni Downloader"
	@echo "✓ Cleaned up Omni Downloader.zip"
