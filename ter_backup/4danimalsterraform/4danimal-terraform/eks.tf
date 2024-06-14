resource "aws_iam_role" "a4danimal" {
  name = "eks-cluster-a4danimal"
  tags = {
    tag-key = "eks-cluster-a4danimal"
  }
    assume_role_policy = <<POLICY
    {
    "Version": "2012-10-17",
    "Statement": [
        {
        "Effect": "Allow",
        "Principal": {
            "Service": ["eks.amazonaws.com"]
        },
        "Action": "sts:AssumeRole"
        }
    ]
}
  POLICY
}
resource "aws_iam_role_policy_attachment" "a4danimal-AmazonEKSClusterPolicy" {
    role = aws_iam_role.a4danimal.name

    policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  
}

# resource "aws_eks_cluster" "a4danimal" {
#   name = "a4danimal"
#   role_arn = aws_iam_role.a4danimal.arn

#   vpc_config {
#     subnet_ids = [
#         aws_subnet.private-us-east-1a.id,
#         aws_subnet.public-us-east-1a.id,
#         aws_subnet.private-us-east-1b.id,
#         aws_subnet.public-us-east-1b.id
#     ]
#   }

#   depends_on = [ aws_iam_role_policy_attachment.a4danimal-AmazonEKSClusterPolicy ]
# }
provider "kubernetes" {
  # config_path = "~/.kube/config"
  host                   = data.aws_eks_cluster.a4danimal.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.a4danimal.certificate_authority.0.data)
  token                  = data.aws_eks_cluster_auth.a4danimal.token
}