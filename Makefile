.PHONY: zip clean

zip: "Omni Downloader.zip"

"Omni Downloader.zip":
	@echo "Creating Omni Downloader.zip..."
	@zip -r "Omni Downloader.zip" package.ini include/ \
		-x "*/RELEASE*.ini" \
		-x "RELEASE.ini" \
		-x "*.pyc" \
		-x "__pycache__/*" \
		-x ".DS_Store" \
		-x "*/.DS_Store"
	@echo "✓ Created Omni Downloader.zip"

clean:
	@rm -f "Omni Downloader.zip"
	@echo "✓ Cleaned up Omni Downloader.zip"
