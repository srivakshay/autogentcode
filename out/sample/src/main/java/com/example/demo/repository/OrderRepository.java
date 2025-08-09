package com.example.demo.repository;

import org.springframework.data.jpa.repository.*;
import com.example.demo.entity.OrderEntity;

public interface OrderRepository extends JpaRepository<OrderEntity, Long> {

}