package com.example.demo.service;

import org.springframework.stereotype.Service;
import com.example.demo.repository.OrderRepository;
import com.example.demo.dto.OrderDto;
import com.example.demo.entity.OrderEntity;

@Service
public class OrderService {

    private final OrderRepository orderRepository;

    public OrderService(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }

    public void createOrder(OrderDto orderDto) {
        OrderEntity orderEntity = OrderMapper.INSTANCE.toEntity(orderDto);
        orderRepository.save(orderEntity);
    }

}