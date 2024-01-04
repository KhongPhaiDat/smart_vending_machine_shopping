provider "aws" {
  region = "ap-northeast-1"
}

# Init storage for tfstate file for multilple devs working
terraform {
  backend "s3" {
    bucket         = "terraform-state-storage-svm-dev"
    key            = "smart-vending-machine/terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "terraform-lock-state"
    encrypt        = true
  }
}

# Init 1 DynamoDB table
resource "aws_dynamodb_table" "menu_database" {
  name           = "Menu_database"
  billing_mode   = "PROVISIONED"
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  ttl {
    attribute_name = ""
    enabled        = false
  }
}
# Init 1 Item in DynamoDB table for testing
resource "aws_dynamodb_table_item" "example" {
  table_name = aws_dynamodb_table.menu_database.name
  hash_key   = aws_dynamodb_table.menu_database.hash_key

  item = <<ITEM
  {
  "id": {
    "S": "ua3dXFyQwMSMzvzEC"
  },
  "items": {
    "M": {
      "bento": {
        "M": {
          "amount": {
            "N": "10"
          },
          "price": {
            "N": "10"
          }
        }
      },
      "chocolate": {
        "M": {
          "amount": {
            "N": "10"
          },
          "price": {
            "N": "10"
          }
        }
      },
      "coffee": {
        "M": {
          "amount": {
            "N": "10"
          },
          "price": {
            "N": "10"
          }
        }
      },
      "cupcake": {
        "M": {
          "amount": {
            "N": "10"
          },
          "price": {
            "N": "10"
          }
        }
      },
      "dat": {
        "M": {
          "amount": {
            "N": "0"
          },
          "price": {
            "N": "0"
          }
        }
      },
      "dried_fruits": {
        "M": {
          "amount": {
            "N": "12"
          },
          "price": {
            "N": "10"
          }
        }
      },
      "gummies": {
        "M": {
          "amount": {
            "N": "10"
          },
          "price": {
            "N": "10"
          }
        }
      },
      "ice_cream": {
        "M": {
          "amount": {
            "N": "10"
          },
          "price": {
            "N": "10"
          }
        }
      },
      "instant_cup_noodle": {
        "M": {
          "amount": {
            "N": "10"
          },
          "price": {
            "N": "10"
          }
        }
      },
      "nuts": {
        "M": {
          "amount": {
            "N": "10"
          },
          "price": {
            "N": "10"
          }
        }
      },
      "orange_juice": {
        "M": {
          "amount": {
            "N": "10"
          },
          "price": {
            "N": "10"
          }
        }
      },
      "salads": {
        "M": {
          "amount": {
            "N": "10"
          },
          "price": {
            "N": "10"
          }
        }
      },
      "sandwiches": {
        "M": {
          "amount": {
            "N": "10"
          },
          "price": {
            "N": "10"
          }
        }
      },
      "soda": {
        "M": {
          "amount": {
            "N": "10"
          },
          "price": {
            "N": "10"
          }
        }
      },
      "sweet_candy": {
        "M": {
          "amount": {
            "N": "10"
          },
          "price": {
            "N": "10"
          }
        }
      },
      "tea": {
        "M": {
          "amount": {
            "N": "10"
          },
          "price": {
            "N": "10"
          }
        }
      },
      "water": {
        "M": {
          "amount": {
            "N": "10"
          },
          "price": {
            "N": "10"
          }
        }
      }
    }
  }
}

ITEM
}
# Init 1 EC2 instance for deploy web app
resource "aws_instance" "smart_vending_machine1" {
  ami           = "ami-0dfa284c9d7b2adad"
  instance_type = "t2.micro"

  iam_instance_profile = aws_iam_instance_profile.ec2_dynamodb.name
  security_groups      = [aws_security_group.allow_streamlit.name]
  tags = {
    Name = "tf_smart_vending_machine1"
  }

  user_data = <<EOF
#!/bin/bash

# Update the package manager and install necessary packages
sudo yum update -y
sudo yum install -y git python3-pip

# Change into ec2-user directory
cd /home/ec2-user
# Clone the Git repository
sudo -u ec2-user git clone https://github.com/KhongPhaiDat/smart_vending_machine_shopping.git

# Change into the repository directory
cd smart_vending_machine_shopping

# Install Python dependencies using pip
sudo -u ec2-user pip3 install -r requirements.txt

# Copy the systemd service file to the appropriate location
sudo cp scripts/streamlit_app.service /etc/systemd/system/

# Reload systemd to pick up the new service file
sudo systemctl daemon-reload

# Start the service
sudo systemctl start streamlit_app

# Enable the service to start on boot
sudo systemctl enable streamlit_app
EOF

  lifecycle {
    create_before_destroy = true
  }
}
# Init IAM role for EC2 to get/write to dynamodb
data "aws_iam_policy_document" "instance_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ec2_dynamodb" {
  name               = "tf_ec2_dynamodb_svm"
  assume_role_policy = data.aws_iam_policy_document.instance_assume_role_policy.json

  inline_policy {
    name = "read_write_dynamodb_table_tf_menu_database"

    policy = jsonencode({
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Sid" : "Stmt1703145729575",
          "Action" : [
            "dynamodb:GetItem",
            "dynamodb:UpdateItem"
          ],
          "Effect" : "Allow",
          "Resource" : "${aws_dynamodb_table.menu_database.arn}"
        }
      ]
    })
  }
}
# Init IAM instance profile with role to get/write data from DynamoDB
resource "aws_iam_instance_profile" "ec2_dynamodb" {
  name = "tf_ec2_dynamodb"
  role = aws_iam_role.ec2_dynamodb.name
}
# Init Security group to allow access from outside to port 8501
resource "aws_security_group" "allow_streamlit" {
  name        = "sg_allow_streamlit_http"
  description = "Allow streamlit inbound traffic"
}
resource "aws_security_group_rule" "outbound_all" {
  type              = "egress"
  to_port           = 0
  protocol          = "-1"
  from_port         = 0
  cidr_blocks       = ["0.0.0.0/0"]
  ipv6_cidr_blocks  = ["::/0"]
  security_group_id = aws_security_group.allow_streamlit.id
}
resource "aws_security_group_rule" "inbound_8501" {
  type                     = "ingress"
  to_port                  = 8501
  protocol                 = "tcp"
  from_port                = 8501
  source_security_group_id = aws_security_group.sg_alb.id
  security_group_id        = aws_security_group.allow_streamlit.id
}
resource "aws_security_group_rule" "inbound_22" {
  type              = "ingress"
  to_port           = 22
  protocol          = "tcp"
  from_port         = 22
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.allow_streamlit.id
}
# Init 1 app load balancer for secure http and connect to EC2
resource "aws_lb" "alb_svm" {
  name               = "alb-svm"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.sg_alb.id]
  subnets            = data.aws_subnets.default_vpc_subnet.ids
}

data "aws_subnets" "default_vpc_subnet" {
  filter {
    name   = "vpc-id"
    values = ["vpc-0f2508234c7d0e246"]
  }
}
resource "aws_lb_target_group" "alb_svm" {
  name     = "alb-svm-tg"
  port     = 8501
  protocol = "HTTP"
  vpc_id   = "vpc-0f2508234c7d0e246"

  lifecycle {
    create_before_destroy = true
  }
}
resource "aws_lb_target_group_attachment" "alb_svm" {
  target_group_arn = aws_lb_target_group.alb_svm.arn
  target_id        = aws_instance.smart_vending_machine1.id
  port             = 8501

  lifecycle {
    create_before_destroy = true
  }
}
# resource "aws_lb_listener" "alb_svm" {
#   load_balancer_arn = aws_lb.alb_svm.arn
#   port              = 80
#   protocol          = "HTTP"

#   default_action {
#     type             = "forward"
#     target_group_arn = aws_lb_target_group.alb_svm.arn
#   }
# }
resource "aws_lb_listener" "alb_svm" {
  load_balancer_arn = aws_lb.alb_svm.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = aws_acm_certificate_validation.cert_validation.certificate_arn
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.alb_svm.arn
  }
}
# Init security group to allow access from outside to port 80
resource "aws_security_group" "sg_alb" {
  name        = "sg_alb_http"
  description = "Allow alb inbound traffic"
}
resource "aws_security_group_rule" "alb_outbound_all" {
  type              = "egress"
  to_port           = 0
  protocol          = "-1"
  from_port         = 0
  cidr_blocks       = ["0.0.0.0/0"]
  ipv6_cidr_blocks  = ["::/0"]
  security_group_id = aws_security_group.sg_alb.id
}
# resource "aws_security_group_rule" "inbound_80" {
#   type              = "ingress"
#   to_port           = 80
#   protocol          = "tcp"
#   from_port         = 80
#   cidr_blocks       = ["0.0.0.0/0"]
#   security_group_id = aws_security_group.sg_alb.id
# }
resource "aws_security_group_rule" "inbound_443" {
  type              = "ingress"
  to_port           = 443
  protocol          = "tcp"
  from_port         = 443
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.sg_alb.id
}
# Init forwarding route from alb to route53 for custom domain
data "aws_route53_zone" "custom_domain" {
  name = "datluyendevops.online."
}
resource "aws_route53_record" "tfsvm" {
  zone_id = data.aws_route53_zone.custom_domain.zone_id
  name    = "svm.${data.aws_route53_zone.custom_domain.name}"
  type    = "A"

  alias {
    name                   = aws_lb.alb_svm.dns_name
    zone_id                = aws_lb.alb_svm.zone_id
    evaluate_target_health = true
  }
}

# Request SSL certificate for custom domain
resource "aws_acm_certificate" "cert" {
  domain_name       = aws_route53_record.tfsvm.name
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}
resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.custom_domain.zone_id
}

resource "aws_acm_certificate_validation" "cert_validation" {
  certificate_arn         = aws_acm_certificate.cert.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}

output "instance_name" {
  value = aws_instance.smart_vending_machine1.tags["Name"]
}
