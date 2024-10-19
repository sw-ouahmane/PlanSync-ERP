from weasyprint import HTML

html_content = '''
<html>
  <head><title>Test PDF</title></head>
  <body><h1>Installation successful!</h1></body>
</html>
'''

# Convert the HTML content to PDF
HTML(string=html_content).write_pdf('test.pdf')
