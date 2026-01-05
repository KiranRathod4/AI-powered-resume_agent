import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO


def export_to_excel(results_list):
    """
    Export multiple resume analysis results to Excel
    
    Args:
        results_list: List of dicts with keys: 'name', 'result'
    
    Returns:
        BytesIO object containing Excel file
    """
    rows = []
    
    for item in results_list:
        name = item['name']
        result = item['result']
        
        row = {
            'Resume': name,
            'Overall Score': result.get('overall_score', 0),
            'Selected': 'Yes' if result.get('selected', False) else 'No',
            'Strengths Count': len(result.get('strengths', [])),
            'Gaps Count': len(result.get('missing_skills', [])),
            'Strengths': ', '.join(result.get('strengths', [])),
            'Missing Skills': ', '.join(result.get('missing_skills', []))
        }
        
        # Add individual skill scores
        skill_scores = result.get('skill_scores', {})
        for skill, score in skill_scores.items():
            row[f'Skill: {skill}'] = score
        
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Resume Analysis', index=False)
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Resume Analysis']
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(str(col))
            )
            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
    
    output.seek(0)
    return output


def export_to_pdf(result, resume_name="Resume"):
    """
    Export single resume analysis to PDF
    
    Args:
        result: Analysis result dict
        resume_name: Name of the resume
    
    Returns:
        BytesIO object containing PDF file
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    # Title
    elements.append(Paragraph(f"Resume Analysis Report", title_style))
    elements.append(Paragraph(f"<b>Candidate:</b> {resume_name}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Overall metrics
    overall_score = result.get('overall_score', 0)
    selected = 'SELECTED ✓' if result.get('selected', False) else 'NOT SELECTED ✗'
    
    data = [
        ['Metric', 'Value'],
        ['Overall Score', f"{overall_score}%"],
        ['Decision', selected],
        ['Strengths', len(result.get('strengths', []))],
        ['Skill Gaps', len(result.get('missing_skills', []))]
    ]
    
    table = Table(data, colWidths=[3*inch, 3*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Skill scores
    elements.append(Paragraph("<b>Skill Breakdown</b>", styles['Heading2']))
    elements.append(Spacer(1, 0.2*inch))
    
    skill_scores = result.get('skill_scores', {})
    if skill_scores:
        skill_data = [['Skill', 'Score (0-10)', 'Status']]
        for skill, score in skill_scores.items():
            status = '✓ Strong' if score >= 7 else '✗ Weak' if score <= 5 else '○ Average'
            skill_data.append([skill, str(score), status])
        
        skill_table = Table(skill_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
        skill_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        elements.append(skill_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def export_comparison_to_pdf(comparison_data):
    """
    Export resume comparison to PDF
    
    Args:
        comparison_data: Dict with 'resume_a', 'resume_b', 'comparison'
    
    Returns:
        BytesIO object containing PDF file
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=20,
        alignment=1
    )
    
    # Title
    elements.append(Paragraph("Resume Comparison Report", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Comparison table
    comp = comparison_data['comparison']
    
    data = [
        ['Metric', 'Resume A', 'Resume B', 'Winner'],
        ['Overall Score', 
         f"{comp['scores']['resume_a']}%", 
         f"{comp['scores']['resume_b']}%",
         comp['winner']],
        ['Strengths', 
         str(comp['strengths_count']['resume_a']),
         str(comp['strengths_count']['resume_b']),
         'A' if comp['strengths_count']['resume_a'] > comp['strengths_count']['resume_b'] else 'B'],
        ['Skill Gaps',
         str(comp['gaps_count']['resume_a']),
         str(comp['gaps_count']['resume_b']),
         'A' if comp['gaps_count']['resume_a'] < comp['gaps_count']['resume_b'] else 'B']
    ]
    
    table = Table(data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    elements.append(table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer