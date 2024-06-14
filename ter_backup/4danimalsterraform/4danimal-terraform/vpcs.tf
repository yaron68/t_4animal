resource "aws_vpc" "a4danimalvpc" {
  cidr_block = "192.168.0.0/16"
  tags = {
    Name = "a4danimalvpc"
  }
}