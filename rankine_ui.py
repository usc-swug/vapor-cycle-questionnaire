import gradio as gr
from rankine import (
    CycleFactory, SimpleRankineCycle, ReheatRankineCycle,
    RegenerativeRankineCycle, RegenerativeReheatRankineCycle
)
import tempfile
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT

def generate_cycle(cycle_type, num_reheats=None, num_fwh=None, case_num=None):
    """Generate and solve a Rankine cycle based on user inputs."""
    try:
        kwargs = {}
        
        if cycle_type == "Simple Rankine Cycle":
            cycle = SimpleRankineCycle()
        elif cycle_type == "Reheat Rankine Cycle":
            if num_reheats is None:
                return "Error: Number of reheats not specified", ""
            cycle = ReheatRankineCycle(num_reheats=int(num_reheats))
        elif cycle_type == "Regenerative Rankine Cycle":
            if num_fwh is None:
                return "Error: Number of FWHs not specified", ""
            cycle = RegenerativeRankineCycle(num_fwh=int(num_fwh))
        elif cycle_type == "Regenerative-Reheat Rankine Cycle":
            if case_num is None:
                return "Error: Case number not specified", ""
            cycle = RegenerativeReheatRankineCycle(case_num=int(case_num))
        else:
            return "Error: Unknown cycle type", ""
        
        cycle.calculate()
        problem = cycle.get_problem_statement()
        solution = cycle.get_solution()
        
        return problem, solution
    
    except Exception as e:
        return f"Error: {str(e)}", ""


def update_parameters(cycle_type):
    """Update visible parameters based on selected cycle type."""
    if cycle_type == "Simple Rankine Cycle":
        return (
            gr.update(visible=False),  # num_reheats
            gr.update(visible=False),  # num_fwh
            gr.update(visible=False),  # case_num
        )
    elif cycle_type == "Reheat Rankine Cycle":
        return (
            gr.update(visible=True),   # num_reheats
            gr.update(visible=False),  # num_fwh
            gr.update(visible=False),  # case_num
        )
    elif cycle_type == "Regenerative Rankine Cycle":
        return (
            gr.update(visible=False),  # num_reheats
            gr.update(visible=True),   # num_fwh
            gr.update(visible=False),  # case_num
        )
    elif cycle_type == "Regenerative-Reheat Rankine Cycle":
        return (
            gr.update(visible=False),  # num_reheats
            gr.update(visible=False),  # num_fwh
            gr.update(visible=True),   # case_num
        )
    else:
        return (
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
        )


def save_results(problem, solution):
    """Create a downloadable PDF file with the problem and solution."""
    if not problem or problem.startswith("Error"):
        return None
    
    # Create a temporary PDF file
    temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
    os.close(temp_fd)
    
    # Create PDF document
    doc = SimpleDocTemplate(temp_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor='#000000',
        spaceAfter=12,
        alignment=TA_LEFT
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        leading=12,
        spaceAfter=6,
        alignment=TA_LEFT,
        fontName='Courier'
    )
    
    # Build PDF content
    story = []
    story.append(Paragraph("Rankine Cycle Analysis", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("Problem Statement", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(problem.replace('\n', '<br/>'), body_style))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("Solution", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(solution.replace('\n', '<br/>'), body_style))
    
    # Build PDF
    doc.build(story)
    
    return temp_path


# Create the Gradio interface
with gr.Blocks(title="Rankine Cycle Problem Generator") as demo:
    gr.Markdown("# Rankine Cycle Problem Generator")
    gr.Markdown("Generate and solve various types of Rankine thermodynamic cycles with random parameters.")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## Configuration")
            
            cycle_type = gr.Dropdown(
                choices=[
                    #"Simple Rankine Cycle",
                    #"Reheat Rankine Cycle",
                    "Regenerative Rankine Cycle",
                    "Regenerative-Reheat Rankine Cycle"
                ],
                value="Simple Rankine Cycle",
                label="Cycle Type",
                interactive=True
            )
            
            num_reheats = gr.Slider(
                minimum=1,
                maximum=2,
                step=1,
                value=1,
                label="Number of Reheats",
                visible=False
            )
            
            num_fwh = gr.Slider(
                minimum=1,
                maximum=2,
                step=1,
                value=1,
                label="Number of Open FWHs",
                visible=False
            )
            
            case_num = gr.Dropdown(
                choices=["1", "2", "3", "4"],
                value="1",
                label="Case Number",
                visible=False
            )
            
            # Update parameters visibility when cycle type changes
            cycle_type.change(
                fn=update_parameters,
                inputs=cycle_type,
                outputs=[num_reheats, num_fwh, case_num]
            )
            
            generate_btn = gr.Button("🚀 Generate Cycle", variant="primary", size="lg")
        
        with gr.Column(scale=2):
            gr.Markdown("## Results")
            
            with gr.Tabs():
                with gr.TabItem("Problem Statement"):
                    problem_output = gr.Textbox(value="", label="Problem", interactive=False, lines=20, max_lines=25)
                
                with gr.TabItem("Solution"):
                    solution_output = gr.Textbox(value="", label="Solution", interactive=False, lines=25, max_lines=40)
            
            with gr.Row():
                download_btn = gr.DownloadButton("💾 Download PDF", variant="secondary")
    
    # Button click handler
    generate_btn.click(
        fn=generate_cycle,
        inputs=[cycle_type, num_reheats, num_fwh, case_num],
        outputs=[problem_output, solution_output]
    )
    
    # Download handler
    download_btn.click(
        fn=save_results,
        inputs=[problem_output, solution_output],
        outputs=download_btn
    )
    
    gr.Markdown("---")
    gr.Markdown(
        """
        ### Cycle Types Explained
        - **Simple Rankine Cycle**: Basic cycle with pump, boiler, turbine, and condenser.
        - **Reheat Rankine Cycle**: Improves efficiency by reheating steam between turbine stages.
        - **Regenerative Rankine Cycle**: Uses open feedwater heaters with steam extraction.
        - **Regenerative-Reheat Cycle**: Combines both reheat and regenerative cycles.
        
        All calculations use water/steam as the working fluid with PYromat thermodynamic properties.
        """
    )


if __name__ == "__main__":
    demo.launch(
        share=False, 
        theme=gr.themes.Monochrome()
    )
