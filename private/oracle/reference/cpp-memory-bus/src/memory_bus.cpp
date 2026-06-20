#include "memory_bus.hpp"

namespace emu {

MemoryFault::MemoryFault(std::uint16_t address, Access access, const char* message)
    : std::runtime_error(message), address_(address), access_(access) {}

void MemoryBus::map_page(std::uint8_t virtual_page, std::uint8_t physical_page, std::uint8_t permissions) {
    pages_[virtual_page] = {true, physical_page, permissions};
    tlb_[virtual_page] = {};
}
void MemoryBus::unmap_page(std::uint8_t virtual_page) {
    pages_[virtual_page] = {};
    tlb_[virtual_page] = {};
}
void MemoryBus::map_mmio(std::uint16_t first, std::uint16_t last, MmioDevice device) {
    if (first > last || !device.read || !device.write) throw std::invalid_argument("invalid MMIO");
    has_mmio_ = true; mmio_first_ = first; mmio_last_ = last; mmio_ = std::move(device);
}
bool MemoryBus::is_mmio(std::uint16_t address) const {
    return has_mmio_ && address >= mmio_first_ && address <= mmio_last_;
}
std::uint16_t MemoryBus::translate(std::uint16_t address, Access access) {
    const auto page = static_cast<std::uint8_t>(address >> 8);
    auto mapping = tlb_[page].valid ? tlb_[page] : (tlb_[page] = pages_[page]);
    const std::uint8_t required =
        access == Access::Read ? R : access == Access::Write ? W : X;
    if (!mapping.valid) throw MemoryFault(address, access, "unmapped");
    if ((mapping.permissions & required) == 0) throw MemoryFault(address, access, "protection");
    return static_cast<std::uint16_t>((mapping.physical << 8) | (address & 0xff));
}
std::array<std::uint16_t, 4> MemoryBus::validate(
    std::uint16_t address, unsigned width, Access access, bool& mmio) {
    std::array<std::uint16_t, 4> physical{};
    mmio = is_mmio(address);
    for (unsigned i = 0; i < width; ++i) {
        auto current = static_cast<std::uint16_t>(address + i);
        if (is_mmio(current) != mmio) throw MemoryFault(current, access, "mixed MMIO and RAM");
        if (!mmio) physical[i] = translate(current, access);
    }
    return physical;
}
std::uint32_t MemoryBus::read_width(std::uint16_t address, unsigned width, Access access) {
    bool device = false;
    auto physical = validate(address, width, access, device);
    std::uint32_t value = 0;
    if (device) value = mmio_.read(address, width);
    else for (unsigned i = 0; i < width; ++i) value |= std::uint32_t(ram_[physical[i]]) << (8 * i);
    cycles_ += device ? 4 : 1;
    return value;
}
void MemoryBus::write_width(std::uint16_t address, unsigned width, std::uint32_t value) {
    bool device = false;
    auto physical = validate(address, width, Access::Write, device);
    if (device) mmio_.write(address, width, value);
    else for (unsigned i = 0; i < width; ++i) ram_[physical[i]] = (value >> (8 * i)) & 0xff;
    cycles_ += device ? 4 : 1;
}
std::uint8_t MemoryBus::read8(std::uint16_t address, Access access) { return read_width(address, 1, access); }
std::uint16_t MemoryBus::read16(std::uint16_t address, Access access) { return read_width(address, 2, access); }
std::uint32_t MemoryBus::read32(std::uint16_t address, Access access) { return read_width(address, 4, access); }
void MemoryBus::write8(std::uint16_t address, std::uint8_t value) { write_width(address, 1, value); }
void MemoryBus::write16(std::uint16_t address, std::uint16_t value) { write_width(address, 2, value); }
void MemoryBus::write32(std::uint16_t address, std::uint32_t value) { write_width(address, 4, value); }
std::uint32_t MemoryBus::fetch_add32(std::uint16_t address, std::uint32_t value) {
    bool device = false;
    auto physical = validate(address, 4, Access::Write, device);
    std::uint32_t before = 0;
    if (device) {
        before = mmio_.read(address, 4);
        mmio_.write(address, 4, before + value);
    } else {
        for (unsigned i = 0; i < 4; ++i) before |= std::uint32_t(ram_[physical[i]]) << (8 * i);
        auto after = before + value;
        for (unsigned i = 0; i < 4; ++i) ram_[physical[i]] = (after >> (8 * i)) & 0xff;
    }
    cycles_ += device ? 4 : 1;
    return before;
}

}
