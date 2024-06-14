
data "aws_eks_cluster" "a4danimal" {
  name = aws_eks_cluster.a4danimal.name
}

resource "aws_eks_cluster" "a4danimal" {
  name = "a4danimal"
  role_arn = aws_iam_role.a4danimal.arn

  vpc_config {
    subnet_ids = [
        aws_subnet.private-us-east-1a.id,
        aws_subnet.public-us-east-1a.id,
        aws_subnet.private-us-east-1b.id,
        aws_subnet.public-us-east-1b.id
    ]
  }

  depends_on = [ aws_iam_role_policy_attachment.a4danimal-AmazonEKSClusterPolicy ]
}

# data "aws_eks_cluster_auth" "a4danimal_cluster_auth" {
data "aws_eks_cluster_auth" "a4danimal" {
  name = data.aws_eks_cluster.a4danimal.name
}

resource "kubernetes_deployment" "a4danimal4app" {
  metadata {
    name      = "a4danimal4app"
    namespace = "default"
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "a4danimal4app"
      }
    }

    template {
      metadata {
        labels = {
          app = "a4danimal4app"
        }
      }

      spec {
        container {
          name  = "a4danimal-app-container"
          image = "andreie/4danimals:latest"
          port {
            container_port = 8081
            host_port = 8081
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "a4danimal_app" {
  metadata {
    name      = "a4danimal-app-service"
    namespace = "default"
  }

  spec {
    selector = {
      app = "a4danimal4app"
    }

    port {
      port        = 80
      target_port = 8081
    }

    type = "LoadBalancer"
  }
}