from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import PythonFile
from difflib import SequenceMatcher
import re
import ast
import networkx as nx


@csrf_exempt
def upload_python_files(request):
    if request.method == 'POST' and 'file1' in request.FILES and 'file2' in request.FILES:
        file1 = request.FILES['file1']
        file2 = request.FILES['file2']

        # Save the files to the database
        python_file = PythonFile.objects.create(file1=file1, file2=file2)
        python_file.save()

        try:
            file1.seek(0)
            file2.seek(0)
            # Read the content of the uploaded files
            file1_content = file1.read().decode('utf-8')
            file2_content = file2.read().decode('utf-8')
            #print(file1_content)
            #print(file2_content)

            # Call each comparison function and collect the results
            results = {
                'type1': type1(file1_content, file2_content),
                'type21': type21(file1_content, file2_content),
                'type22': type22(file1_content, file2_content),
                'type31': type31(file1_content, file2_content)[1],  # Only the similarity value
                'type32': type32(file1_content, file2_content)[1],  # Only the similarity value
                'typ33': typ33(file1_content, file2_content)[1]    # Only the similarity value
            }
                        
            return JsonResponse({'message': 'Files uploaded successfully!', 'results': results})

        except Exception as e:
            return JsonResponse({'error': f"Error reading files: {str(e)}"}, status=500)

    return JsonResponse({'error': 'Invalid request or missing files'}, status=400)




# Create your views here.
def home(request):
    return render(request, 'home.html')
def contactus(request):
    return render(request, 'contactus.html')
def about(request):
    return render(request, 'about.html')
def main(request):
    return render(request, 'app.html')

def type1(content1, content2):
    """Compare two strings (file contents) and return a similarity ratio."""
    similarity = SequenceMatcher(None, content1, content2).ratio()
    print(similarity)
    return similarity

def type21(code1: str, code2: str, threshold=0.8):
    def normalize_code(code):
        code = re.sub(r"#.*", "", code)  # Remove single-line comments
        code = re.sub(r"\s+", " ", code)  # Normalize whitespace
        return code.strip()

    # Normalize the input code strings
    normalized_code1 = normalize_code(code1)
    normalized_code2 = normalize_code(code2)

    # Compute similarity
    similarity = SequenceMatcher(None, normalized_code1, normalized_code2).ratio()

    # Return the result
    return similarity

def type22(code1: str, code2: str):
    def get_ast_structure(code):
        # Parse the code and return its Abstract Syntax Tree (AST) as a string
        return ast.dump(ast.parse(code))

    # Get the AST structures for both code snippets
    ast1 = get_ast_structure(code1)
    ast2 = get_ast_structure(code2)

    # Compare the ASTs
    return ast1 == ast2

def type31(code1: str, code2: str, threshold=0.6):
    def build_cfg(code):
        try:
            parsed_code = ast.parse(code)
            graph = nx.DiGraph()

            def add_node_and_edge(node):
                if isinstance(node, (ast.If, ast.For, ast.While)):
                    graph.add_node(node)

                    # Connect control flow edges (simplified example)
                    if hasattr(node, 'body') and isinstance(node.body, list) and node.body:
                        next_node = node.body[0]
                        graph.add_edge(node, next_node)

            for node in ast.walk(parsed_code):
                add_node_and_edge(node)

            return graph
        except Exception as e:
            print(f"Error parsing code: {e}")
            return nx.DiGraph()  # Return an empty graph if an error occurs

    # Build CFGs for both code snippets
    cfg1 = build_cfg(code1)
    cfg2 = build_cfg(code2)

    # Skip comparison if either CFG is empty
    if len(cfg1.nodes) == 0 or len(cfg2.nodes) == 0:
        return False, 0.0

    # Compute similarity using node intersection
    common_nodes = set(cfg1.nodes).intersection(cfg2.nodes)
    similarity = len(common_nodes) / float(len(cfg1.nodes) + len(cfg2.nodes) - len(common_nodes))

    # Return whether they are clones and their similarity
    return similarity >= threshold, similarity

def normalize_control_flow_from_code(code):
    try:
        parsed_code = ast.parse(code)
        control_flow_structure = []
        for node in ast.walk(parsed_code):
            if isinstance(node, (ast.If, ast.For, ast.While)):
                control_flow_structure.append(type(node).__name__)
        return control_flow_structure
    except:
        return []

def type32(code1, code2, threshold=0.8):
    control_flow1 = normalize_control_flow_from_code(code1)
    control_flow2 = normalize_control_flow_from_code(code2)

    # Skip comparison if either code doesn't have any control flow structures
    if not control_flow1 or not control_flow2:
        return False, 0.0

    common = len(set(control_flow1).intersection(control_flow2))
    similarity = common / float(len(set(control_flow1).union(control_flow2)))
    return similarity >= threshold, similarity

def normalize_code_semantics_from_string(code):
    # Remove all comments, string literals, and normalize whitespaces
    code = re.sub(r"#.*", "", code)  # Remove comments
    code = re.sub(r'\'[^\']*\'|"[^"]*"', "<string>", code)  # Replace string literals with <string>
    code = re.sub(r"\s+", " ", code)  # Normalize whitespaces
    return code.strip()

def typ33(code1, code2, threshold=0.8):
    normalized_code1 = normalize_code_semantics_from_string(code1)
    normalized_code2 = normalize_code_semantics_from_string(code2)
    similarity = SequenceMatcher(None, normalized_code1, normalized_code2).ratio()
    return similarity >= threshold, similarity