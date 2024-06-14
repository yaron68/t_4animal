resource "aws_iam_role" "nodes" {
  name = "eks-node-group-nodes"
  assume_role_policy = jsonencode({
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }],
    Version = "2012-10-17"
  })
}
# resource "aws_iam_role_policy_attachment" "node-AmazonEKSWorkNodePolicy" {
#   policy_arn = "arn:aws:iam:aws:policy/AmazonEKSWorkNodePolicy"
#   role = aws_iam_role.nodes.name
# }
# resource "aws_iam_role_policy_attachment" "node-AmazonEKSCNIPolicy" {
#   policy_arn = "arn:aws:iam:aws:policy/AmazonEKS_CNI_Policy"
#   role = aws_iam_role.nodes.name
# }
resource "aws_iam_role_policy_attachment" "node-AmazonEKSWorkNodePolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy" 
  role       = aws_iam_role.nodes.name
}

resource "aws_iam_role_policy_attachment" "node-AmazonEKSCNIPolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"  
  role       = aws_iam_role.nodes.name
}




resource "aws_iam_role_policy_attachment" "node-AmazonEC2ContainerRegistryReadOnly" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.nodes.name
}
# resource "aws_eks_node_group" "private_nodes" {
    # cluster_name = aws_eks_cluster.a4danimal.node_group_name
resource "aws_eks_node_group" "private_nodes" {
    cluster_name = "a4danimal"
    node_group_name = "privet_nodes"
    node_role_arn = aws_iam_role.nodes.arn
    subnet_ids = [aws_subnet.private-us-east-1a.id, aws_subnet.private-us-east-1b.id]
    capacity_type = "ON_DEMAND"
    instance_types = ["t2.micro"]
    scaling_config {
        desired_size = 2
        max_size = 10
        min_size = 2
        }
    update_config {
        max_unavailable = 2
    }

labels = {
    node = "kubenode02"
    }
depends_on = [aws_iam_role_policy_attachment.node-AmazonEC2ContainerRegistryReadOnly, 
              aws_iam_role_policy_attachment.node-AmazonEKSCNIPolicy,
              aws_iam_role_policy_attachment.node-AmazonEKSWorkNodePolicy]
}
data "tls_certificate" "eks" {
    url = aws_eks_cluster.a4danimal.identity[0].oidc[0].issuer
}
resource "aws_iam_openid_connect_provider" "eks" {
  client_id_list = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.eks.certificates[0].sha1_fingerprint]
  url = aws_eks_cluster.a4danimal.identity[0].oidc[0].issuer
}
data "aws_iam_policy_document" "eks_cluster_autoscaler_assume_roll_policy" {
    statement{
        actions = ["sts:AssumeRoleWithWebIdentity"]
        effect = "Allow"
        condition  {
            test = "StringEquals"
            # variable = "${replace(aws_iam_openid_connect_provider.eks.url,"https://","")}:sub"
            variable = "${replace(aws_eks_cluster.a4danimal.identity[0].oidc[0].issuer, "https://", "")}:sub"

            values =  ["system.serviceaccount:kube-system:cluster-autoscaler"]
        }
        principals {
                identifiers = [aws_iam_openid_connect_provider.eks.arn]
                type = "Federated"
            }
    }
}
resource "aws_iam_role" "eks_cluster_autoscaler" {
    assume_role_policy = data.aws_iam_policy_document.eks_cluster_autoscaler_assume_roll_policy.json
    name = "eks-cluster-autoscaler"
}
