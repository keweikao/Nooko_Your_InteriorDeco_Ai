import pdfplumber
import openpyxl
from fastapi import UploadFile
import io
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ParsingService:
    """
    A service dedicated to parsing different file formats (PDF, Excel)
    to extract quote information.
    """

    async def parse_quote_file(self, file: UploadFile) -> Dict[str, Any]:
        """
        Parses the content of an uploaded quote file.

        :param file: The uploaded file from FastAPI.
        :return: A dictionary containing the parsed data.
        """
        content_type = file.content_type
        logger.info(f"Parsing file: {file.filename} with content type: {content_type}")
        
        file_content = await file.read()
        
        try:
            if "pdf" in content_type:
                return self._parse_pdf(io.BytesIO(file_content))
            elif "spreadsheetml" in content_type or "excel" in content_type:
                return self._parse_excel(io.BytesIO(file_content))
            else:
                logger.warning(f"Unsupported content type: {content_type}")
                return {"error": f"Unsupported file type: {content_type}"}
        except Exception as e:
            logger.error(f"Failed to parse file {file.filename}: {e}", exc_info=True)
            return {"error": f"Failed to process file: {str(e)}"}

    def _parse_pdf(self, file_stream: io.BytesIO) -> Dict[str, Any]:
        """
        Parses a PDF file and extracts all text.
        """
        text_content = []
        with pdfplumber.open(file_stream) as pdf:
            for page in pdf.pages:
                text_content.append(page.extract_text() or "")
        
        full_text = "\n".join(text_content)
        logger.info(f"Successfully extracted {len(full_text)} characters from PDF.")
        # For now, we return the raw text. Later tasks will structure this.
        return {"raw_text": full_text}

    def _parse_excel(self, file_stream: io.BytesIO) -> Dict[str, Any]:
        """
        Parses an Excel file and extracts data from the active sheet.
        """
        workbook = openpyxl.load_workbook(file_stream)
        sheet = workbook.active
        
        data = []
        for row in sheet.iter_rows(values_only=True):
            # Filter out empty rows
            if any(cell is not None for cell in row):
                data.append(list(row))
        
        logger.info(f"Successfully extracted {len(data)} rows from Excel file.")
        # For now, we return the raw data. Later tasks will structure this.
        return {"rows": data}

# Singleton instance
parsing_service = ParsingService()
